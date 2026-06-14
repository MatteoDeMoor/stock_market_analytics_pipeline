import os

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://www.alphavantage.co/query"


def fetch_daily_prices(symbol: str) -> dict:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY not found. Check your .env file.")

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
    }

    response = requests.get(BASE_URL, params=params, timeout=30)

    print(f"Fetching daily prices for symbol: {symbol}")
    print(f"Status code: {response.status_code}")

    response.raise_for_status()

    data = response.json()

    if "Error Message" in data:
        raise ValueError(f"API error: {data['Error Message']}")

    if "Note" in data:
        raise ValueError(f"API limit message: {data['Note']}")

    if "Information" in data:
        raise ValueError(f"API information message: {data['Information']}")

    if "Time Series (Daily)" not in data:
        raise ValueError("Unexpected API response: missing 'Time Series (Daily)'.")

    return data
