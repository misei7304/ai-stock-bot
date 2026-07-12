def generate_recommendation_reason(stock, market_result):
    from strategy_management.config import get_strategy_config

    config = get_strategy_config()
    rsi_limit = config["rsi_limit"]

    reasons = []

    if market_result["is_market_bull"]:
        reasons.append("시장 상태가 상승장입니다.")
    else:
        reasons.append("시장 상태가 약세장입니다.")

    if stock["rsi"] >= 50 and stock["rsi"] < rsi_limit:
        reasons.append("RSI가 과열 구간은 아니면서 상승 흐름을 보입니다.")
    elif stock["rsi"] >= rsi_limit:
        reasons.append("RSI가 전략 기준상 과열 구간에 있습니다.")
    else:
        reasons.append("RSI 상승 강도가 약합니다.")

    if stock["macd"] > stock["macd_signal"]:
        reasons.append("MACD가 Signal 위에 있어 단기 추세가 우위입니다.")
    else:
        reasons.append("MACD가 Signal 아래에 있어 추세가 약합니다.")

    if stock["atr_percent"] < 6:
        reasons.append("ATR%가 과도하게 높지 않아 변동성이 관리 가능한 수준입니다.")
    else:
        reasons.append("ATR%가 높아 변동성 리스크가 있습니다.")

    if stock["final_score"] >= 50:
        reasons.append("최종점수가 양호합니다.")
    else:
        reasons.append("최종점수가 아직 강한 매수 수준은 아닙니다.")

    return " ".join(reasons)