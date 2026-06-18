AI Stock Bot

Overview

AI Stock Bot is an AI-driven stock analysis, recommendation, observation, and strategy-learning system for the Korean stock market.

The system automatically:

* Downloads stock data from Yahoo Finance
* Calculates technical indicators
* Evaluates market conditions using KOSPI
* Generates stock recommendations
* Performs historical backtesting
* Simulates portfolio growth
* Tracks real recommendation performance
* Stores recommendation history in SQLite
* Sends daily email reports
* Learns from losing recommendations
* Generates strategy improvement suggestions
* Blocks real trading until risk requirements are satisfied
* Saves strategy evolution suggestions
* Analyzes strategy improvement history

The goal is to build a self-improving stock recommendation engine before enabling real-money trading.

⸻

Main Features

Data Collection

* Yahoo Finance
* Historical OHLCV data
* Daily stock updates

⸻

Technical Indicators

* MA5
* MA20
* Volume MA5
* Volume MA20
* RSI (14)
* MACD (12,26)
* MACD Signal (9)
* MACD Histogram
* Bollinger Bands (20,2)
    * Upper Band
    * Middle Band
    * Lower Band
* ATR (14)
* ATR Percent
* ATR Score

⸻

Market Regime Analysis

KOSPI is analyzed before generating recommendations.

Bull Market:

KOSPI Current Price > KOSPI MA20

Bear Market:

KOSPI Current Price < KOSPI MA20

Rules:

* Bull market → recommendations allowed
* Bear market → recommendations blocked

⸻

Stock Scoring System

Base Score Components:

* Price Score
* Volume Score
* MACD Score
* Bollinger Score
* ATR Score

Additional Adjustments:

* Sector Bonus
* Adaptive Bonus
* Sector Penalty
* Factor Penalty
* Recommendation Reason Score

Final Score:

Final Score determines ranking priority.

⸻

Buy Candidate Conditions

A stock becomes a buy candidate when:

* Current Price > MA5
* MA5 > MA20
* Total Score > 0
* RSI < active strategy rsi_limit
* MACD > MACD Signal
* Market is Bullish

⸻

Recommendation Reason Engine

The system automatically generates human-readable explanations.

Example:

* Market is bullish
* RSI shows healthy momentum
* MACD is above Signal
* ATR volatility risk exists
* Final score is strong

These explanations are stored and later analyzed.

⸻

Backtesting Engine

Entry Conditions:

* Current Price > MA5
* MA5 > MA20
* RSI < active strategy rsi_limit
* MACD > MACD Signal

Exit Conditions:

* Take Profit = ATR × 3.0
* Stop Loss = ATR × 1.5
* Maximum Holding Period = 5 trading days

Configurable through .env

⸻

Account Simulation

Starting Capital:

1,000,000 KRW

Outputs:

* Final Asset Value
* Total Profit
* Simulated Growth

⸻

Risk Management

Capital and risk allocation are configurable.

Calculates:

* Available Capital
* Position Size
* Share Quantity
* Investment Amount
* Buy Availability

⸻

Real Trading Safety Guard

The system blocks real trading until sufficient evidence exists.

Current Requirements:

* Minimum 20 recommendations
* Stable recommendation success rate
* Positive strategy score

If requirements are not met:

* Real trading disabled
* Observation mode only

⸻

Observation Mode

When real trading is blocked:

* Top 3 candidates are selected
* Observation database is updated
* Observation email is sent
* No actual trading recommendation is allowed

⸻

Recommendation Types

Every recommendation is categorized.

Current Types:

* real
* observation

real

Used when:

* Real trading is allowed
* Risk guard passes

observation

Used when:

* Real trading is blocked
* Observation mode is active

Each recommendation type is stored in SQLite.

This allows separate performance tracking for:

* Real recommendations
* Observation recommendations

⸻

Recommendation Database

SQLite Database:

stock_bot.db

Stores:

* Recommendations
* Recommendation Types
* Performance Tracking
* Recommendation Reasons
* Strategy Versions
* Market Conditions

⸻

Recommendation Performance Tracking

Tracks:

* Recommendation Price
* Current Price
* Current Return
* 1-Day Return
* 5-Day Return
* 20-Day Return

Updates automatically every day.

⸻

Real Performance Analysis

Analyzes:

* Success Rate
* Average Return
* Best Return
* Worst Return

⸻

Recommendation Type Performance Analysis

Performance is analyzed by recommendation type.

Metrics:

* Recommendation Count
* Success Rate
* Average Return
* Best Return
* Worst Return

Example:

[observation]

* Recommendations: 50
* Success Rate: 58%
* Average Return: 1.8%

[real]

* Recommendations: 30
* Success Rate: 67%
* Average Return: 3.1%

This helps determine whether observation recommendations should be promoted to real trading.

⸻

Market Performance Analysis

Performance grouped by:

* Bull Market
* Bear Market

⸻

Sector Performance Analysis

Tracks:

* Semiconductor
* Finance
* Automobile
* Battery
* Chemical
* Internet
* Bio
* Steel
* Holdings

Measures:

* Recommendation Count
* Success Rate
* Average Return

⸻

Factor Performance Analysis

Analyzes performance by:

RSI Range

* 30~40
* 40~50
* 50~60
* 60~70

MACD Range

* 0~500
* 500~1000
* 1000~2000
* 2000+

ATR Percent Range

* 0~2%
* 2~4%
* 4~6%
* 6~8%
* 8%+

Bollinger Score

* +3
* 0
* -3

Final Score

* Below 0
* 0~30
* 30~50
* 50~70
* 70~100
* 100+

⸻

Losing Pattern Analyzer

Automatically analyzes losing recommendations.

Examples:

* Repeated sector losses
* High ATR losses
* RSI pattern losses
* Bollinger pattern losses

⸻

Strategy Optimization Engine

Generates automatic improvement suggestions.

Example Suggestions:

* Increase semiconductor penalty
* Strengthen ATR risk filter
* Tighten RSI entry range
* Increase Bollinger penalties

Currently:

Observation Only

No automatic strategy modification is performed.

⸻

Strategy Evolution History

The system stores daily strategy improvement suggestions in SQLite.

It prevents duplicate strategy suggestions from being saved on the same day.

Stores:

* Evolution Date
* Strategy Suggestion Text
* Created Timestamp

Analyzes:

* Recent strategy improvement history
* Previously generated suggestions
* Strategy learning progress over time

This allows the system to track how the strategy evolves before real trading is enabled.

⸻

Strategy Version Tracking

Every recommendation stores the strategy version that generated it.

Example:

v1.0.0
v1.1.0
v1.2.0

Stored Information:

* Strategy Version
* Recommendation Date
* Recommendation Performance

This allows historical comparison between strategy versions.

The system can later determine:

* Which strategy version performs best
* Success rate by version
* Average return by version
* Evolution effectiveness

Current Version:

v1.1.0

⸻

Strategy Configuration

Each active strategy version can use different parameter settings.

Current Configurations:

v1.0.0

* RSI Limit: 70
* ATR Penalty Threshold: 8
* Factor Penalty: -4

v1.1.0

* RSI Limit: 65
* ATR Penalty Threshold: 7
* Factor Penalty: -5

The system automatically loads the configuration from the currently active strategy version.

This allows strategy behavior to change by version without manually rewriting core logic.

The active strategy configuration is printed in the terminal output at runtime and included in observation email reports.

⸻

Strategy Version Performance Analysis

Performance is analyzed separately for each strategy version.

Metrics:

* Recommendation Count
* Success Rate
* Average Return
* Best Return
* Worst Return

Example:

[v1.0.0]

* Recommendations: 25
* Success Rate: 64%
* Average Return: 2.3%

This allows objective evaluation of strategy upgrades.

⸻

Strategy Version Comparison

The system compares the currently active strategy version with the previous strategy version.

Comparison metrics:

* Current Strategy Version
* Previous Strategy Version
* Average Return Change
* Improvement Difference
* Better Performing Version
* Confidence Level

Confidence Level:

* Low: fewer than 20 total recommendations
* Medium: fewer than 100 total recommendations
* High: 100 or more total recommendations

The comparison is printed in the terminal output and included in observation email reports.

This helps determine whether a newly activated strategy version is actually improving performance over the previous version.

⸻

Strategy Upgrade Workflow

The system supports a manual strategy upgrade workflow.

Workflow:

1. Generate strategy improvement suggestions
2. Save valid suggestions as strategy upgrade candidates
3. Review pending candidates
4. Approve reviewed candidates
5. Create a new strategy version from an approved candidate
6. Activate the new strategy version

Candidate Status Flow:

pending → reviewed → approved → version_created

The system does not automatically apply new strategies without review and approval.

This prevents weak or incomplete suggestions from changing the active strategy.

⸻

Email Reporting

Two Email Modes:

Trading Email

Sent only when:

* Real trading allowed

Contains:

* Recommended stock
* Position sizing
* Risk analysis
* Market condition

Observation Email

Sent when:

* Real trading blocked

Contains:

* Top 3 observation candidates
* Recommendation reasons
* Strategy version information
* Strategy version performance
* Recommendation type performance
* Strategy optimization suggestions
* Risk warnings
* Strategy upgrade candidates
* Strategy version comparison

⸻

CSV Reports

Generated Files:

* stock_report.csv
* history.csv

⸻

Database

Database File:

stock_bot.db

Tables include:

* recommendations
* recommendation_performance
* strategy_versions
* strategy_evolution
* strategy_upgrade_candidates
* email_logs

Key Recommendation Fields:

* recommendation_reason
* strategy_version
* recommendation_type
* market_name
* market_bull

⸻

Automatic Daily Execution

Runs automatically through launchd.

Current Schedule:

Every Day at 09:00

Execution Script:

./run.sh

⸻

Environment Variables

EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password
TO_EMAIL=your_email@example.com

CAPITAL=1000000
RISK_RATIO=0.3

BUY_FEE_RATE=0.00015
SELL_FEE_RATE=0.00195

ATR_STOP_MULTIPLIER=1.5
ATR_TAKE_PROFIT_MULTIPLIER=3.0

⸻

Technologies

* Python
* pandas
* yfinance
* sqlite3
* python-dotenv
* smtplib
* launchd

⸻

Future Improvements

* Telegram Notifications
* Discord Notifications
* Machine Learning Ranking Models
* Portfolio Optimization
* Dynamic Position Sizing
* Portfolio Rebalancing
* Multi-Stock Portfolio Simulation
* AI-Based Factor Discovery
* Automated Strategy Adjustment (After Sufficient Validation)
* Real Trading API Integration
* Web Dashboard
* Mobile Dashboard