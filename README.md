AI Stock Bot

Overview

AI Stock Bot is a Python-based stock analysis, backtesting, recommendation, and risk management system for the Korean stock market.

The program:

* Downloads stock data from Yahoo Finance
* Calculates technical indicators
* Identifies buy candidates
* Performs historical backtesting
* Simulates account growth
* Generates CSV reports
* Saves recommendation history
* Tracks recommendation performance
* Updates current return automatically
* Analyzes strategy performance
* Ranks stock performance by average return
* Sends daily email reports
* Calculates position sizing based on available capital
* Runs automatically every day

⸻

Project Structure

ai-stock-bot/
│
├── main.py
├── data.py
├── strategy.py
├── backtest.py
├── stocks.py
├── report.py
├── history.py
├── history_analyzer.py
├── performance.py
├── strategy_performance.py
├── email_sender.py
├── risk.py
│
├── run.sh
├── requirements.txt
├── .env
│
├── stock_report.csv
├── history.csv
│
└── README.md

⸻

Features

Data Collection

* Yahoo Finance API
* Historical stock data

Technical Indicators

* 5-day Moving Average (MA5)
* 20-day Moving Average (MA20)
* 5-day Volume Average
* 20-day Volume Average
* RSI (14)
* MACD
* MACD Signal
* MACD Histogram
* Bollinger Bands
  * Upper Band
  * Middle Band
  * Lower Band

Strategy

Buy candidate conditions:

* Current Price > MA5
* MA5 > MA20
* Total Score > 0
* RSI < 70
* MACD > MACD Signal

MACD bonus:

* +5 score when MACD > MACD Signal

Bollinger bonus:

* +3 score when price is near lower band
* -3 score when price is near upper band

Backtesting

Entry rules:

* Current Price > MA5
* MA5 > MA20
* MACD > MACD Signal

Exit rules:

* Take Profit: +10%
* Stop Loss: -5%
* Maximum Holding Period: 5 Days

Account Simulation

Starting Capital:

* 1,000,000 KRW

Outputs:

* Final Asset Value
* Total Profit

Risk Management

Position sizing:

* Capital: configurable through .env
* Risk Allocation: configurable through .env

Automatically calculates:

* Available investment amount
* Number of shares that can be purchased
* Actual investment amount
* Buy availability

Recommendation Logic

Selection process:

1. Generate buy candidates
2. Rank by final score
3. Filter stocks that cannot be purchased with available capital
4. Recommend the highest-ranked affordable stock

Reporting

Creates:

* stock_report.csv
* history.csv

stock_report.csv includes:

* RSI
* MACD
* MACD Signal
* MACD Histogram
* Bollinger Upper Band
* Bollinger Middle Band
* Bollinger Lower Band
* Bollinger Score
* Final Score
* Win Rate
* Average Return
* Final Asset Value

History Analysis

Tracks:

* Recommended stocks
* Recommendation count
* Recommendation dates

Recommendation Performance Tracking

Tracks:

* Recommendation price
* Current price
* Current return
* 1-day return
* 5-day return
* 20-day return
* Updates current return in history.csv

Strategy Performance Summary

Tracks:

* Total recommendation count
* Recommendation count by stock
* Average return by stock
* Success rate by stock
* Stock performance ranking by average return

Success condition:

* Current return > 0

Email Notification

Sends a daily email report including:

* Best recommended stock
* Buy candidate ranking
* Risk management summary
* Current price
* Final score
* RSI
* MACD
* MACD Signal
* MACD Histogram
* Bollinger Upper Band
* Bollinger Middle Band
* Bollinger Lower Band
* Bollinger Score
* Backtest win rate
* Average return
* Final simulated asset value
* Buy availability
* Recommended position size

Automatic Daily Execution

Runs automatically using macOS launchd.

Current schedule:

* Every day at 09:00

Execution script:

./run.sh

⸻

Environment Variables

Create a .env file:

EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password
TO_EMAIL=your_email@example.com
CAPITAL=1000000
RISK_RATIO=0.3

Variables

Variable	Description
EMAIL_ADDRESS	Sender email address
EMAIL_PASSWORD	Email password or app password
TO_EMAIL	Recipient email address
CAPITAL	Total available capital
RISK_RATIO	Percentage of capital allocated per trade

Example:

CAPITAL=1000000
RISK_RATIO=0.3

Available investment amount:

1,000,000 × 30% = 300,000 KRW

⸻

Example Output

* Buy Candidate Ranking
* Backtest Performance Ranking
* Best Stock Recommendation
* Recommendation History Summary
* Recommendation Performance Tracking
* Strategy Performance Summary
* Stock Performance Ranking
* MACD Metrics
* Bollinger Band Analysis
* Risk Management Summary
* Daily Email Report

⸻

Technologies

* Python
* yfinance
* pandas
* python-dotenv
* smtplib
* CSV
* launchd

⸻

Future Improvements

* Telegram Notifications
* Portfolio Optimization
* Machine Learning Models
* Real Trading Integration
* Advanced Risk Management
* Dynamic Position Sizing
* Multi-Stock Portfolio Backtesting
* AI-Based Stock Selection
* Portfolio Rebalancing
* Market Regime Detection
* Database Integration
* Web Dashboard