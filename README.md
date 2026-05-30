# Stock Analytics Dashboard 

A full stack stock analytics dashboard built with FastAPI, Snowflake, and Chart.js.

## Live Demo
[Click here to view](https://stock-analytics-snowflake-production.up.railway.app/dashboard)

## Tech Stack
- **Data Source** — Alpha Vantage API
- **Data Warehouse** — Snowflake
- **Backend** — Python, FastAPI
- **Frontend** — HTML, CSS, JavaScript, Chart.js
- **Containerization** — Docker
- **Deployment** — Railway

## Features
- Real-time stock data for AAPL, GOOGL and TSLA
- Interactive price chart with historical trends
- 7 day moving average and price change tracking
- Search any stock symbol

## How to Run
```bash
git clone https://github.com/sssimransingh26-bit/stock-analytics-snowflake.git
cd stock-analytics-snowflake
pip install -r requirements.txt
# Add your credentials to .env file
uvicorn main:app --reload
```

## Run with Docker
```bash
docker build -t stock-analytics .
docker run -p 8000:8000 --env-file .env stock-analytics
```

## Author
— [GitHub](https://github.com/sssimransingh26-bit)
