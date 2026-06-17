AI Stock Bot

Overview

AI Stock Bot is a Python-based stock analysis and backtesting project.

The program:

* Downloads stock data from Yahoo Finance
* Calculates technical indicators
* Identifies buy candidates
* Performs historical backtesting
* Simulates account growth
* Generates CSV reports
* Saves recommendation history
* Tracks recommendation performance

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
│
├── stock_report.csv
├── history.csv
├── requirements.txt
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

Strategy

Buy candidate conditions:

* Current Price > MA5
* MA5 > MA20
* Total Score > 0
* RSI < 70

Backtesting

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

Reporting

Creates:

* stock_report.csv
* history.csv

History Analysis

Tracks:

* Recommended stocks
* Recommendation count
* Recommendation dates

Performance Tracking

Tracks:

* Recommendation price
* Current price
* Recommendation return (%)

⸻

Example Output

* Buy Candidate Ranking
* Backtest Performance Ranking
* Best Stock Recommendation
* Recommendation History Summary
* Recommendation Performance Tracking

⸻

Technologies

* Python
* yfinance
* Pandas
* CSV

⸻

Future Improvements

* MACD Indicator
* Bollinger Bands
* Automatic Daily Execution
* Email Notifications
* Telegram Notifications
* Portfolio Optimization
* Machine Learning Models
* Real Trading Integration
* Risk Management System