from strategy_management.config import get_strategy_config


def get_factor_penalty(stock):
    config = get_strategy_config()

    penalty = 0
    factor_penalty = config["factor_penalty"]
    atr_penalty_threshold = config["atr_penalty_threshold"]

    if stock["rsi"] >= 50 and stock["rsi"] < 60:
        penalty -= 2

    if stock["atr_percent"] >= atr_penalty_threshold:
        penalty += factor_penalty

    if stock["bollinger_score"] == -3:
        penalty -= 2

    return penalty


def apply_factor_penalty(stock):
    factor_penalty = get_factor_penalty(stock)

    stock["factor_penalty"] = factor_penalty
    stock["final_score"] = stock["final_score"] + factor_penalty

    return stock