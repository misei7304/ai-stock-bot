from storage.database import get_connection


def get_strategy_optimization_suggestions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.sector_name,
            r.rsi,
            r.atr_percent,
            r.bollinger_score,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND p.current_return < 0
    """)

    rows = cursor.fetchall()
    connection.close()

    suggestions = []

    if len(rows) < 3:
        suggestions.append("손실 데이터가 아직 부족합니다.")
        suggestions.append("최소 3개 이상의 손실 추천 기록이 쌓이면 개선 제안을 생성합니다.")
        return suggestions

    sector_losses = {}
    high_atr_count = 0
    rsi_50_60_count = 0
    bollinger_minus_3_count = 0

    for sector_name, rsi, atr_percent, bollinger_score, current_return in rows:
        sector_losses[sector_name] = sector_losses.get(sector_name, 0) + 1

        if atr_percent >= 6:
            high_atr_count += 1

        if 50 <= rsi < 60:
            rsi_50_60_count += 1

        if bollinger_score == -3:
            bollinger_minus_3_count += 1

    suggestions.append("[최근 손실 패턴]")

    has_pattern = False

    for sector_name, count in sector_losses.items():
        if count >= 2:
            suggestions.append(f"- {sector_name} 섹터 손실 반복: {count}회")
            has_pattern = True

    if high_atr_count >= 2:
        suggestions.append(f"- ATR% 6 이상 구간 손실 반복: {high_atr_count}회")
        has_pattern = True

    if rsi_50_60_count >= 2:
        suggestions.append(f"- RSI 50~60 구간 손실 반복: {rsi_50_60_count}회")
        has_pattern = True

    if bollinger_minus_3_count >= 2:
        suggestions.append(f"- 볼린저 점수 -3 구간 손실 반복: {bollinger_minus_3_count}회")
        has_pattern = True

    if not has_pattern:
        suggestions.append("- 아직 반복 손실 패턴이 뚜렷하지 않습니다.")

    suggestions.append("")
    suggestions.append("[권장 조치]")

    has_action = False

    for sector_name, count in sector_losses.items():
        if count >= 2:
            suggestions.append(f"- {sector_name} 섹터 패널티 강화 검토")
            has_action = True

    if high_atr_count >= 2:
        suggestions.append("- ATR% 6 이상 종목 패널티 강화 검토")
        has_action = True

    if rsi_50_60_count >= 2:
        suggestions.append("- RSI 50~60 구간 진입 조건 재검토")
        has_action = True

    if bollinger_minus_3_count >= 2:
        suggestions.append("- 볼린저 점수 -3 종목 감점 강화 검토")
        has_action = True

    if not has_action:
        suggestions.append("- 현재는 자동 전략 변경 없이 관찰만 유지합니다.")

    suggestions.append("")
    suggestions.append("주의: 아직 자동 적용하지 말고 관찰만 합니다.")

    return suggestions


def analyze_strategy_optimization_suggestions():
    print("\n" + "#" * 80)
    print("자동 전략 개선 제안")
    print("#" * 80)

    suggestions = get_strategy_optimization_suggestions()

    for suggestion in suggestions:
        print(suggestion)