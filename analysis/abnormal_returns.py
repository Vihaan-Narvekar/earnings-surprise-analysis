import pandas as pd
import datetime
from config import CAR_WINDOWS, MARKET_TICKER
from data.price_data import get_price_data
import numpy as np
import statsmodels.api as sm
import traceback

def calculate_abnormal_returns(ticker, earnings_df):
    abnormal_returns_list = []
    
    for idx, row in earnings_df.iterrows():
        try:
            # Get the event date and ensure it's timezone-naive
            event_date = row['Date']
            if not isinstance(event_date, (pd.Timestamp, datetime)):
                try:
                    event_date = pd.to_datetime(event_date)
                except:
                    print(f"Could not convert {event_date} to datetime")
                    continue
                    
            # Remove timezone info if present
            if hasattr(event_date, 'tz') and event_date.tz is not None:
                event_date = event_date.tz_localize(None)
                
           
                
            start_date = event_date - datetime.timedelta(days=120)
            end_date = event_date + datetime.timedelta(days=max(CAR_WINDOWS) + 5)

            stock_prices = get_price_data(ticker, start_date, end_date)
            market_prices = get_price_data(MARKET_TICKER, start_date, end_date)

            if stock_prices.empty or market_prices.empty:
                print(f"Insufficient price data for {ticker} around {event_date}")
                continue

            # Ensure dates align between stock and market
            # Combine into a single DataFrame
            combined_index = stock_prices.index.union(market_prices.index)
            prices = pd.DataFrame(index=combined_index)
            prices['stock'] = stock_prices
            prices['market'] = market_prices
            
            # Drop rows with missing data
            prices = prices.dropna()

            if len(prices) < 30:  # Ensure enough data for regression
                print(f"Insufficient aligned price data for {ticker} around {event_date}: only {len(prices)} points")
                continue
                
            # Calculate returns
            returns = prices.pct_change().dropna()

            # Find the closest date to the event date in the returns index
            returns_dates = returns.index.to_pydatetime()
            
            # Make sure event_date is a datetime object
            if isinstance(event_date, pd.Timestamp):
                event_timestamp = event_date.to_pydatetime()
            else:
                event_timestamp = event_date
                
            # Calculate time differences in days
            time_diffs = np.array([(d - event_timestamp).total_seconds() / (24*3600) for d in returns_dates])
            
            # Find the closest date after or on the event date
            valid_diffs = time_diffs[time_diffs >= 0]
            if len(valid_diffs) == 0:
                print(f"No trading days on or after event date {event_date}")
                continue
                
            closest_diff_idx = np.argmin(valid_diffs)
            closest_idx = np.where(time_diffs >= 0)[0][closest_diff_idx]
            event_loc = closest_idx
            
            # Verify we have the right date
            event_trading_date = returns.index[event_loc]
            
            
            # Estimation window should end before event
            estimation_end = event_loc - 1
            if estimation_end <= 0:
                print(f"No pre-event data available for {ticker} on {event_date}")
                continue
                
            # Estimate market model using pre-event window
            estimation_returns = returns.iloc[:estimation_end].copy()
            
            if len(estimation_returns) < 20:
                print(f"Insufficient estimation period for {ticker} on {event_date}: only {len(estimation_returns)} points")
                continue
                
            # Market Model Regression
            X = sm.add_constant(estimation_returns['market'])
            y = estimation_returns['stock']
            model = sm.OLS(y, X).fit()
            
            # Calculate abnormal returns for entire period
            X_full = sm.add_constant(returns['market'])
            returns['expected'] = model.predict(X_full)
            returns['abnormal'] = returns['stock'] - returns['expected']

            for window in CAR_WINDOWS:
                try:
                    # Calculate post-event window
                    start_idx = event_loc + 1  # Start day after the event
                    end_idx = min(start_idx + window, len(returns))
                    
                    if end_idx - start_idx < window * 0.7:  # Allow for some missing trading days
                        print(f"Insufficient post-event data for {window}-day window: only {end_idx - start_idx} points")
                        continue
                        
                    post_event_returns = returns.iloc[start_idx:end_idx]
                    car = post_event_returns['abnormal'].sum()
                    
                    # Extract surprise value safely
                    surprise = None
                    if 'Surprise' in row and not pd.isna(row['Surprise']):
                        surprise = row['Surprise']
                    elif 'Surprise(%)' in row and not pd.isna(row['Surprise(%)']):
                        surprise = row['Surprise(%)'] / 100
                    
                    if surprise is None:
                        print(f"No valid surprise value for {ticker} on {event_date}")
                        continue
                        
                    result_dict = {
                        'Ticker': ticker,
                        'EventDate': event_date,
                        'CAR_Window': window,
                        'CAR': car,
                        'Surprise': surprise,
                    }
                    
                    # Add other columns if available
                    if 'EPS Estimate' in row and not pd.isna(row['EPS Estimate']):
                        result_dict['EPS_Estimate'] = row['EPS Estimate']
                    if 'Reported EPS' in row and not pd.isna(row['Reported EPS']):
                        result_dict['Reported_EPS'] = row['Reported EPS']
                        
                    abnormal_returns_list.append(result_dict)
                    
                    
                except Exception as e:
                    print(f"Error calculating CAR for {ticker} on {event_date}: {e}")
                    traceback.print_exc()
                    
        except Exception as e:
            print(f"Error processing event for {ticker} at index {idx}: {e}")
            traceback.print_exc()
    
    # Check if we have any results before creating DataFrame        
    if not abnormal_returns_list:
        print(f"No valid abnormal returns calculated for {ticker}")
        return pd.DataFrame()
        
    return pd.DataFrame(abnormal_returns_list)