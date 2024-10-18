# stock_data/utils.py

import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import StockData

def fetch_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={settings.ALPHA_VANTAGE_API_KEY}"
    
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError("Invalid response from Alpha Vantage API")

    time_series = data["Time Series (Daily)"]
    two_years_ago = datetime.now() - timedelta(days=730)

    for date_str, daily_data in time_series.items():
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if date < two_years_ago.date():
            break

        StockData.objects.update_or_create(
            symbol=symbol,
            date=date,
            defaults={
                'open_price': daily_data['1. open'],
                'high_price': daily_data['2. high'],
                'low_price': daily_data['3. low'],
                'close_price': daily_data['4. close'],
                'volume': daily_data['5. volume'],
            }
        )
