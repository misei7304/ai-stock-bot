AI Stock Bot

Overview

AI Stock Bot is a Python-based stock analysis, backtesting, and recommendation system for the Korean stock market.

The program:

* Downloads stock data from Yahoo Finance
* Calculates technical indicators
* Identifies buy candidates
* Performs historical backtesting
* Simulates account growth
* Generates CSV reports
* Saves recommendation history
* Tracks recommendation performance
* Sends daily email reports
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

Recommendation Performance Tracking

Tracks:

* Recommendation price
* Current price
* Current return
* 1-day return
* 5-day return
* 20-day return

Strategy Performance Summary

Tracks:

* Total recommendation count
* Recommendation count by stock

Email Notification

Sends a daily email report including:

* Best recommended stock
* Buy candidate ranking
* Current price
* Final score
* RSI
* Backtest win rate
* Average return
* Final simulated asset value

Automatic Daily Execution

Runs automatically using macOS launchd.

Current schedule:

* Every day at 09:00

Execution script:

./run.sh

⸻

Example Output

* Buy Candidate Ranking
* Backtest Performance Ranking
* Best Stock Recommendation
* Recommendation History Summary
* Recommendation Performance Tracking
* Strategy Performance Summary
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

* MACD Indicator
* Bollinger Bands
* Telegram Notifications
* Portfolio Optimization
* Machine Learning Models
* Real Trading Integration
* Risk Management System
* Position Sizing System
* Multi-Stock Portfolio Backtesting
* AI-Based Stock Selection