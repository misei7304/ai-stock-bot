from database import get_connection


def analyze_strategy_optimization_suggestions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.company_name,
            r.ticker,
            r.sector_name,
            r.final_score,
            r.rsi,
            r.macd,
            r.macd_signal,
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

    print("\n" + "#" * 80)
    print("자동 전략 개선 제안")
    print("#" * 80)

    if len(rows) < 3:
        print("손실 데이터가 아직 부족합니다.")
        print("최소 3개 이상의 손실 추천 기록이 쌓이면 개선 제안을 생성합니다.")
        return

    sector_losses = {}
    high_atr_count = 0
    rsi_50_60_count = 0
    bollinger_minus_3_count = 0

    for row in rows:
        (
            company_name,
            ticker,
            sector_name,
            final_score,
            rsi,
            macd,
            macd_signal,
            atr_percent,
            bollinger_score,
            current_return,
        ) = row

        if sector_name not in sector_losses:
            sector_losses[sector_name] = 0

        sector_losses[sector_name] += 1

        if atr_percent >= 6:
            high_atr_count += 1

        if 50 <= rsi < 60:
            rsi_50_60_count += 1

        if bollinger_score == -3:
            bollinger_minus_3_count += 1

    print("\n최근 손실 패턴")

    for sector_name, count in sector_losses.items():
        if count >= 2:
            print(f"- {sector_name} 섹터 손실 반복: {count}회")

    if high_atr_count >= 2:
        print(f"- ATR% 6 이상 구간 손실 반복: {high_atr_count}회")

    if rsi_50_60_count >= 2:
        print(f"- RSI 50~60 구간 손실 반복: {rsi_50_60_count}회")

    if bollinger_minus_3_count >= 2:
        print(f"- 볼린저 점수 -3 구간 손실 반복: {bollinger_minus_3_count}회")

    print("\n권장 조치")

    for sector_name, count in sector_losses.items():
        if count >= 2:
            print(f"- {sector_name} 섹터 패널티 강화 검토")

    if high_atr_count >= 2:
        print("- ATR% 6 이상 종목 패널티 강화 검토")

    if rsi_50_60_count >= 2:
        print("- RSI 50~60 구간 진입 조건 재검토")

    if bollinger_minus_3_count >= 2:
        print("- 볼린저 점수 -3 종목 감점 강화 검토")

    print("\n주의: 아직 자동 적용하지 말고 관찰만 합니다.")