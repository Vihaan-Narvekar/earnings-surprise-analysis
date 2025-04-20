import pandas as pd
import numpy as np
import traceback
import yfinance as yf

def get_earnings_calendar(ticker):
    try:
        stock = yf.Ticker(ticker)
        print(f"Retrieving earnings data for {ticker}...")
        
        # Get earnings dates
        earnings = stock.get_earnings_dates(limit=20)
        
        if earnings is None or earnings.empty:
            print(f"No earnings data found for {ticker}")
            return pd.DataFrame()
            
   
        
        # Create a proper DataFrame ensuring we have the date
        if isinstance(earnings, pd.DataFrame):
            earnings_df = earnings.copy()
            
            # Check if the index is the date
            if isinstance(earnings_df.index, pd.DatetimeIndex):
                earnings_df = earnings_df.reset_index()
                if earnings_df.columns[0] == 'Earnings Date':
                    earnings_df.rename(columns={'Earnings Date': 'Date'}, inplace=True)
                else:
                    earnings_df.rename(columns={earnings_df.columns[0]: 'Date'}, inplace=True)
        else:
            # Handle unexpected return type
            print(f"Unexpected data type for earnings: {type(earnings)}")
            return pd.DataFrame()
            
        # If we still don't have a Date column, try to find it
        if 'Date' not in earnings_df.columns:
            date_column_candidates = ['Earnings Date', 'earnings_date', 'date', 'Date']
            for col in date_column_candidates:
                if col in earnings_df.columns:
                    earnings_df.rename(columns={col: 'Date'}, inplace=True)
                    break
                    
        # If still no Date column, we may need to create the DataFrame differently
        if 'Date' not in earnings_df.columns and isinstance(earnings.index, pd.DatetimeIndex):
            earnings_df = pd.DataFrame({
                'Date': earnings.index,
                'EPS Estimate': earnings['EPS Estimate'] if 'EPS Estimate' in earnings.columns else np.nan,
                'Reported EPS': earnings['Reported EPS'] if 'Reported EPS' in earnings.columns else np.nan,
                'Surprise(%)': earnings['Surprise(%)'] if 'Surprise(%)' in earnings.columns else np.nan
            })
            
        # Final check if we have Date column
        if 'Date' not in earnings_df.columns:
            print(f"Error: Could not find or create Date column for {ticker}")
            return pd.DataFrame()
            
        # Ensure Date is datetime without timezone
        earnings_df['Date'] = pd.to_datetime(earnings_df['Date']).dt.tz_localize(None)
        
        # Filter out future dates
        today = pd.Timestamp.today().normalize()
        earnings_df = earnings_df[earnings_df['Date'] <= today]
        
        # Sort by date descending (most recent first)
        earnings_df = earnings_df.sort_values('Date', ascending=False)
        
        # Process Surprise data
        if 'Surprise(%)' in earnings_df.columns:
            earnings_df['Surprise'] = earnings_df['Surprise(%)'] / 100
        elif 'Surprise' not in earnings_df.columns:
            earnings_df['Surprise'] = np.nan
            
        # Add ticker
        earnings_df['Ticker'] = ticker
        
        # Ensure required columns exist
        for col in ['EPS Estimate', 'Reported EPS']:
            if col not in earnings_df.columns:
                earnings_df[col] = np.nan
                
        # Clean missing values
        earnings_df = earnings_df.dropna(subset=['Date'])
        # Make EPS columns optional since we only need Surprise for analysis
        valid_earnings = earnings_df[~pd.isna(earnings_df['Surprise'])]
        
        if not valid_earnings.empty:
            print(f"Retrieved {len(valid_earnings)} valid earnings records with surprise values for {ticker}")
            return valid_earnings
        else:
            print(f"Retrieved earnings data but no valid surprise values for {ticker}")
            return earnings_df
            
    except Exception as e:
        print(f"Error retrieving earnings for {ticker}: {e}")
        traceback.print_exc()
        return pd.DataFrame()