from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
import snowflake.connector
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()
conn=None

@asynccontextmanager
async def lifespan(app:FastAPI):
    global conn
    try:
        conn=snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
        )
        print("Snowflake connected successfully")
    except Exception as e:
        print(f"Failed to connect snowflake:{e}")
    yield
    if conn:
        conn.close()
        print("Snowflake connection closed")

app=FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/dashboard")
def dashboard():
    return FileResponse("index.html")


@app.get("/")
def home():
    return {"message":"Stock analysis API is running"}

@app.get("/stocks/{symbol}")
def get_stock(symbol:str):
    try:
        cursor=conn.cursor()
        cursor.execute("""
                   SELECT SYMBOL,TRADE_DATE,OPEN_PRICE,HIGH_PRICE,LOW_PRICE,CLOSE_PRICE,VOLUME
                   FROM STOCK_PRICES
                   WHERE SYMBOL=%s
                   ORDER BY TRADE_DATE DESC
                   LIMIT 30
                   """,(symbol.upper()))
        rows=cursor.fetchall()
        cursor.close()

        if not rows:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol.upper()}")

        return {"symbol": symbol.upper(), "data": [
            {
                "date": str(row[1]),
                "open": row[2],
                "high": row[3],
                "low": row[4],
                "close": row[5],
                "volume": row[6]
            } for row in rows
        ]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/stocks/{symbol}/analytics")
def get_analytics(symbol:str):
    try:
        cursor=conn.cursor()
        cursor.execute("""
            SELECT TRADE_DATE,CLOSE_PRICE, ROUND(CLOSE_PRICE-OPEN_PRICE,2) AS PRICE_CHANGE,
            ROUND (((CLOSE_PRICE - OPEN_PRICE)/OPEN_PRICE)*100,2) AS PERCENT_CHANGE,
            AVG(CLOSE_PRICE) OVER (ORDER BY TRADE_DATE 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) AS MOVING_AVG_7DAY
            FROM STOCK_PRICES
            WHERE SYMBOL = %s
            ORDER BY TRADE_DATE DESC
            LIMIT 30
        """, (symbol.upper()))

        rows=cursor.fetchall()
        cursor.close()

        if not rows:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol.upper()}")

        return {"symbol":symbol.upper(),"analytics":[
            {
                "date": str(row[0]),#dates are not always json serialzable
                "close": row[1],
                "price_change": row[2],
                "percent_change": row[3],
                "moving_avg_7day": round(row[4], 2)
            }for row in rows
        ]}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


