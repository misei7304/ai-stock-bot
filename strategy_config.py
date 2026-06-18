from strategy_version import get_current_strategy_version


def get_strategy_config():
    version = get_current_strategy_version()

    if version == "v1.0.0":
        return {
            "rsi_limit": 70,
            "atr_penalty_threshold": 8,
            "factor_penalty": -4,
        }

    if version == "v1.1.0":
        return {
            "rsi_limit": 65,
            "atr_penalty_threshold": 7,
            "factor_penalty": -5,
        }

    return {
        "rsi_limit": 70,
        "atr_penalty_threshold": 8,
        "factor_penalty": -4,
    }

def get_strategy_config_summary():
    config = get_strategy_config()

    return [
        f"RSI 제한: {config['rsi_limit']}",
        f"ATR 패널티 기준: {config['atr_penalty_threshold']}%",
        f"팩터 패널티: {config['factor_penalty']}",
    ]