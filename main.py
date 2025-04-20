# earnings_surprise_pead_project.py
"""
Full project pipeline for:
"The Impact of Earnings Surprises on Post-Announcement Drift in U.S. Equities"

This script will:
1. Fetch earnings dates & EPS data
2. Collect stock and market price data
3. Calculate abnormal returns
4. Compute cumulative abnormal returns (CARs)
5. Run regression analysis on CARs vs earnings surprises

Author: Vihaan Narvekar
Date: April 2025
"""

import os
import statsmodels.api as sm
import datetime
import seaborn as sns
import traceback
from matplotlib import pyplot as plt

from config import TICKERS, OUTPUT_DIR, CAR_WINDOWS
from data.earnings_data import get_earnings_calendar
from analysis.abnormal_returns import calculate_abnormal_returns
import pandas as pd

def run_pipeline():
    all_abnormal_returns = []
    
    for ticker in TICKERS:
        print(f"\nProcessing {ticker}...")
        earnings_df = get_earnings_calendar(ticker)
        
        if earnings_df.empty:
            print(f"Skipping {ticker} due to missing earnings data")
            continue
            
        abnormal_returns = calculate_abnormal_returns(ticker, earnings_df)
        
        if not abnormal_returns.empty:
            all_abnormal_returns.append(abnormal_returns)
            print(f"Successfully calculated abnormal returns for {ticker}")
        else:
            print(f"No valid abnormal returns generated for {ticker}")
    
    # Check if we have any valid results        
    if not all_abnormal_returns:
        print("No valid abnormal returns data to concatenate. Check tickers or earnings availability.")
        return pd.DataFrame()
        
    all_data = pd.concat(all_abnormal_returns, ignore_index=True)
    print(f"\nFinal dataset contains {len(all_data)} observations across {len(all_data['Ticker'].unique())} tickers")
    return all_data

def analyze_results(data):
    # Check if we have any data to analyze
    if data.empty:
        print("No data available for analysis")
        return pd.DataFrame()
        
    # Create results directory if it doesn't exist
    os.makedirs("output/figures", exist_ok=True)
    
    results_summary = []
    
    # Analysis by window
    for window in CAR_WINDOWS:
        window_data = data[data['CAR_Window'] == window].copy()
        
        if len(window_data) < 10:
            print(f"Insufficient data for {window}-day window analysis (only {len(window_data)} observations)")
            continue
            
        # Remove outliers
        q1 = window_data['CAR'].quantile(0.05)
        q3 = window_data['CAR'].quantile(0.95)
        window_data_clean = window_data[(window_data['CAR'] >= q1) & (window_data['CAR'] <= q3)]
        
        print(f"\nAnalyzing {window}-day CAR with {len(window_data_clean)} observations (after removing outliers)")
        
        # Run regression
        X = sm.add_constant(window_data_clean['Surprise'])
        y = window_data_clean['CAR']
        model = sm.OLS(y, X).fit()
        
        print(f"\nRegression Results for {window}-Day CAR:")
        print(model.summary().tables[1])
        
        results_summary.append({
            'Window': window,
            'Coefficient': model.params['Surprise'],
            'P-Value': model.pvalues['Surprise'],
            'R-squared': model.rsquared,
            'N': len(window_data_clean)
        })
        
        # Create scatter plot
        plt.figure(figsize=(10, 6))
        plt.scatter(window_data_clean['Surprise'], window_data_clean['CAR'], alpha=0.5)
        plt.plot(window_data_clean['Surprise'], model.predict(), 'r-', linewidth=2)
        plt.title(f'Earnings Surprise vs {window}-Day CAR')
        plt.xlabel('Earnings Surprise')
        plt.ylabel(f'{window}-Day Cumulative Abnormal Return')
        plt.grid(True, alpha=0.3)
        plt.savefig(f"output/figures/car_{window}day_scatter.png")
        plt.close()
    
    # Check if we have any results    
    if not results_summary:
        return pd.DataFrame()
        
    results_df = pd.DataFrame(results_summary)
    print("\nSummary of Results:")
    print(results_df)
    return results_df

def save_output(data, results_df):
    # Check if we have data to save
    if data.empty:
        print("No data to save")
        return
        
    # Save the full dataset
    data.to_csv("output/earnings_drift_results.csv", index=False)
    
    # Save the summary results if available
    
    results_df.to_csv("output/regression_results_summary.csv", index=False)
    

    print("\nAnalysis complete. Results saved to output directory.")

# ======================== REGRESSION ANALYSIS ========================
def run_regression_analysis(car_df):
    """Perform regression analysis of CARs against earnings surprises."""
    try:
        if car_df.empty:
            print("No CAR data available for regression.")
            return
        
        print("\nRunning regression analysis on CARs vs. Earnings Surprises...\n")
        
        for window in CAR_WINDOWS:
            window_df = car_df[car_df['CAR_Window'] == window].copy()
            if len(window_df) < 5:
                print(f"Not enough data for {window}-day CAR regression (n={len(window_df)})")
                continue
            
            X = window_df[['Surprise']]
            y = window_df['CAR']
            
            # Statsmodels for detailed regression output
            X_const = sm.add_constant(X)
            model = sm.OLS(y, X_const).fit()
            print(f"\n--- Regression Results for {window}-Day CAR ---")
            print(model.summary())

            # Plotting the regression
            plt.figure(figsize=(8, 5))
            sns.regplot(data=window_df, x='Surprise', y='CAR', ci=95, scatter_kws={'s': 50})
            plt.title(f'{window}-Day CAR vs. Earnings Surprise')
            plt.xlabel('Earnings Surprise')
            plt.ylabel('Cumulative Abnormal Return (CAR)')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"output/CAR_vs_Surprise_{window}D.png")
            plt.close()
            
    except Exception as e:
        print(f"Error in regression analysis: {e}")
        traceback.print_exc()


# ======================== MAIN ========================
if __name__ == '__main__':
    try:
        print("Starting Earnings Surprise and PEAD Analysis Pipeline...")
        data = run_pipeline()
        if not data.empty:
            results_df = analyze_results(data)
            save_output(data, results_df)
            print("\nAnalysis completed successfully!")
        else:
            print("\nNo data was generated. Please check the logs for errors.")
    except Exception as e:
        print(f"Pipeline failed: {e}")
        traceback.print_exc()

        
    all_car_results = []

    for ticker in TICKERS:
        earnings_df = get_earnings_calendar(ticker)
        if earnings_df.empty:
            continue
        
        car_df = calculate_abnormal_returns(ticker, earnings_df)
        if not car_df.empty:
            all_car_results.append(car_df)
    
    if all_car_results:
        final_df = pd.concat(all_car_results, ignore_index=True)
        final_df.to_csv("output/CAR_Results.csv", index=False)
        print("\nSaved all CAR results to output/CAR_Results.csv")

        # Run regression analysis
        run_regression_analysis(final_df)
    else:
        print("No CAR data generated for any tickers.")
