import requests
import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY=os.getenv("ALPHA_VANTAGE_API_KEY")
SYMBOLS=["AAPL" ,"GOOGL", "TSLA"]

conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
)

cursor = conn.cursor()
cursor.execute("DELETE FROM STOCK_PRICES WHERE SYMBOL = %s", [SYMBOL])

for SYMBOL in SYMBOLS:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={SYMBOL}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    time_series = data.get("Time Series (Daily)", {})

    for date, values in time_series.items():
        cursor.execute("""
        INSERT INTO STOCK_PRICES 
        (SYMBOL, TRADE_DATE, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        SYMBOL,
        date,
        float(values["1. open"]),
        float(values["2. high"]),
        float(values["3. low"]),
        float(values["4. close"]),
        int(values["5. volume"])
    ))

    print(f"loaded {len(time_series)} records for {SYMBOL}")


conn.commit()
cursor.close()
conn.close()

print("All stocks loaded completely");