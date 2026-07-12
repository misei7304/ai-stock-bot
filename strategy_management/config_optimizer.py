from strategy_management.config import get_strategy_config
from performance_analysis.loss_analyzer import get_losing_recommendations


def get_strategy_config_optimization_summary():
    config = get_strategy_config()

    summary = []

    losing_recommendations = get_losing_recommendations()

    if len(losing_recommendations) < 3:
        summary.append("전략 설정 자동 튜닝 보류")
        summary.append("이유: 손실 추천 데이터가 3개 미만입니다.")
        summary.append(f"현재 RSI 제한: {config['rsi_limit']:g}")
        summary.append(f"현재 ATR 패널티 기준: {config['atr_penalty_threshold']:g}%")
        summary.append(f"현재 팩터 패널티: {config['factor_penalty']:g}")
        return summary

    avg_rsi = sum(item["rsi"] for item in losing_recommendations) / len(losing_recommendations)
    avg_atr_percent = sum(item["atr_percent"] for item in losing_recommendations) / len(losing_recommendations)

    new_rsi_limit = config["rsi_limit"]
    new_atr_penalty_threshold = config["atr_penalty_threshold"]
    new_factor_penalty = config["factor_penalty"]

    if avg_rsi >= config["rsi_limit"] - 5:
        new_rsi_limit = max(50, config["rsi_limit"] - 5)

    if avg_atr_percent >= config["atr_penalty_threshold"]:
        new_atr_penalty_threshold = max(4, config["atr_penalty_threshold"] - 1)

    if avg_atr_percent >= config["atr_penalty_threshold"]:
        new_factor_penalty = config["factor_penalty"] - 1

    summary.append("전략 설정 자동 튜닝 제안")
    summary.append(f"손실 추천수: {len(losing_recommendations)}회")
    summary.append(f"손실 평균 RSI: {avg_rsi:.2f}")
    summary.append(f"손실 평균 ATR%: {avg_atr_percent:.2f}%")
    summary.append("")
    summary.append(f"RSI 제한: {config['rsi_limit']:g} → {new_rsi_limit:g}")
    summary.append(
        f"ATR 패널티 기준: "
        f"{config['atr_penalty_threshold']:g}% → {new_atr_penalty_threshold:g}%"
    )
    summary.append(f"팩터 패널티: {config['factor_penalty']:g} → {new_factor_penalty:g}")

    if (
        new_rsi_limit == config["rsi_limit"]
        and new_atr_penalty_threshold == config["atr_penalty_threshold"]
        and new_factor_penalty == config["factor_penalty"]
    ):
        summary.append("판단: 현재 설정 유지")
    else:
        summary.append("판단: 다음 전략 버전에 위 설정 적용 검토")

    return summary


def analyze_strategy_config_optimization():
    print("\n" + "#" * 80)
    print("전략 설정 자동 튜닝 제안")
    print("#" * 80)

    summary = get_strategy_config_optimization_summary()

    for line in summary:
        print(line)