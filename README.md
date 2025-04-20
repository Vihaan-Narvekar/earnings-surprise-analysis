# The Impact of Earnings Surprises on Post-Announcement Drift

This project analyzes how earnings surprises affect post-earnings announcement drift (PEAD) for large-cap U.S. equities. We use a market model to estimate expected returns and compute cumulative abnormal returns (CARs) over 5, 10, and 30-day windows.

## Pipeline
1. Collect EPS surprise and historical earnings calendar
2. Fetch stock and market prices from Yahoo Finance
3. Estimate abnormal returns via OLS market model
4. Calculate CARs for short-, medium-, and long-term horizons
5. Regress CARs against surprise magnitudes

## How to Run
```bash
python earnings_surprise_pead_project.py
