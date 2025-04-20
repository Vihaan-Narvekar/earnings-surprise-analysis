import yfinance as yf
import pandas as pd


def get_price_data(ticker, start_date, end_date):
    """Fetch price data for a ticker between start and end dates."""
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
        
        if data.empty:
            print(f"No price data available for {ticker}")
            return pd.Series()
            
        # Use Adj Close for returns calculation
        return data['Adj Close']
    except Exception as e:
        print(f"Error fetching price data for {ticker}: {e}")
        return pd.Series()
