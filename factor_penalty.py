from database import get_connection


def get_factor_penalty(stock):
    penalty = 0

    if stock["rsi"] >= 50 and stock["rsi"] < 60:
        penalty -= 2

    if stock["atr_percent"] >= 6 and stock["atr_percent"] < 8:
        penalty -= 2

    if stock["bollinger_score"] == -3:
        penalty -= 2

    return penalty


def apply_factor_penalty(stock):
    factor_penalty = get_factor_penalty(stock)

    stock["factor_penalty"] = factor_penalty
    stock["final_score"] = stock["final_score"] + factor_penalty

    return stock