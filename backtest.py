def backtest(data):

    trades = []

    for i in range(20, len(data) - 5):

        current_price = data["Close"].iloc[i]

        ma5 = data["MA5"].iloc[i]
        ma20 = data["MA20"].iloc[i]

        if current_price > ma5 and ma5 > ma20:

            buy_price = current_price

            sell_price = None

            for j in range(1, 6):

                future_price = data["Close"].iloc[i + j]

                profit = (
                    (future_price - buy_price)
                    / buy_price
                ) * 100

                if profit >= 10:
                    sell_price = future_price
                    break

                if profit <= -5:
                    sell_price = future_price
                    break

            if sell_price is None:
                sell_price = data["Close"].iloc[i + 5]

            final_profit = (
                (sell_price - buy_price)
                / buy_price
            ) * 100

            trades.append(final_profit)

    return trades


def analyze_backtest(trades):
    if len(trades) == 0:
        return {
            "trade_count": 0,
            "win_rate": 0,
            "average_return": 0,
            "total_return": 0,
            "best_trade": 0,
            "worst_trade": 0,
        }

    wins = 0

    for trade in trades:
        if trade > 0:
            wins += 1

    win_rate = (wins / len(trades)) * 100
    average_return = sum(trades) / len(trades)

    total_return = 1

    for trade in trades:
        total_return *= (1 + trade / 100)

    total_return = (total_return - 1) * 100

    best_trade = max(trades)
    worst_trade = min(trades)

    return {
        "trade_count": len(trades),
        "win_rate": win_rate,
        "average_return": average_return,
        "total_return": total_return,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
    }


def simulate_account(trades):
    money = 1000000

    for trade in trades:
        money = money * (1 + trade / 100)

    profit = money - 1000000

    return {
        "start_money": 1000000,
        "final_money": money,
        "profit": profit,
    }