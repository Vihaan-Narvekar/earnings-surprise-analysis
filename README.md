# The Impact of Earnings Surprises on Post-Announcement Drift in U.S. Equities

This research project investigates the relationship between earnings surprises and post-earnings announcement drift (PEAD) in U.S. equities. It explores whether stocks with greater earnings surprises systematically experience abnormal returns following earnings announcements, using event-study methodology and regression analysis.

---

## Project Motivation

Post-earnings announcement drift (PEAD) is a well-documented anomaly in financial markets. Despite being known for decades, its persistence challenges market efficiency theories. By quantifying the relationship between earnings surprises and abnormal returns after announcements, this project aims to provide new insights into market behavior and pricing inefficiencies.

---

## Methodology Overview

1. **Data Collection**
   - Historical price and earnings data sourced via Yahoo Finance or financial APIs.
   - Earnings surprise calculated as:
     \[
     \text{Earnings Surprise (\%)} = \frac{\text{Actual EPS} - \text{Estimated EPS}}{|\text{Estimated EPS}|} \times 100
     \]

2. **Event Study Setup**
   - Defines an event window around earnings announcements.
   - Calculates abnormal returns using a market model with a specified estimation window.
   - Cumulative Abnormal Returns (CARs) are computed for each stock-event.

3. **Statistical Analysis**
   - Cross-sectional regression:
     \[
     \text{CAR}_{[t_1,t_2]} = \alpha + \beta \cdot \text{Earnings Surprise} + \varepsilon
     \]
   - Evaluation of statistical significance and robustness.

---

## Tech Stack

- **Language**: Python
- **Libraries**:
  - `pandas`, `numpy` — data processing
  - `matplotlib`, `seaborn` — visualization
  - `statsmodels`, `scipy` — statistical modeling
  - `yfinance` — data collection


---

## Key Visuals

- Relationship between earnings surprise and CAR
- Distribution of abnormal returns across time
- Regression diagnostics and confidence intervals

---

## Key Findings

- **Positive correlation** between earnings surprises and CARs over [t+1, t+5] windows.
- Results support the existence of **market underreaction** to earnings news.
- Drift persists even after controlling for outliers and varying estimation window lengths.

---

## Getting Started

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt

    Run the analysis
        python main.py
        Check reports and outputs
        Navigate to the outputs/ and reports/ folders for visualizations and final insights.

This project is licensed under the MIT License. See LICENSE for more information.


