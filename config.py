import os

TICKERS = ["AAPL", "NVDA", "GOOGL", "PLTR"]  # Users can change this list
MARKET_TICKER = "^GSPC"  # S&P 500 index
CAR_WINDOWS = [1, 2, 5, 10, 30]  # Days after earnings to measure drift
OUTPUT_DIR = "output"
os.makedirs("output", exist_ok=True)


