from storage.database import get_connection


def analyze_losing_patterns():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.company_name,
            r.ticker,
            r.final_score,
            r.rsi,
            r.macd,
            r.macd_signal,
            r.atr_percent,
            r.bollinger_score,
            r.sector_name,
            r.market_bull,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND p.current_return < 0
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("손실 추천 패턴 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 손실 추천 데이터가 없습니다.")
        connection.close()
        return

    total_count = len(rows)

    rsi_values = []
    macd_gap_values = []
    atr_percent_values = []
    final_score_values = []

    sector_stats = {}
    market_stats = {}

    for row in rows:
        (
            company_name,
            ticker,
            final_score,
            rsi,
            macd,
            macd_signal,
            atr_percent,
            bollinger_score,
            sector_name,
            market_bull,
            current_return,
        ) = row

        rsi_values.append(rsi)
        macd_gap_values.append(macd - macd_signal)
        atr_percent_values.append(atr_percent)
        final_score_values.append(final_score)

        if sector_name not in sector_stats:
            sector_stats[sector_name] = []

        sector_stats[sector_name].append(current_return)

        market_name = "상승장" if market_bull == 1 else "약세장"

        if market_name not in market_stats:
            market_stats[market_name] = []

        market_stats[market_name].append(current_return)

    print(f"손실 추천수: {total_count}회")
    print(f"손실 추천 평균 RSI: {sum(rsi_values) / total_count:.2f}")
    print(f"손실 추천 평균 MACD Gap: {sum(macd_gap_values) / total_count:.2f}")
    print(f"손실 추천 평균 ATR%: {sum(atr_percent_values) / total_count:.2f}%")
    print(f"손실 추천 평균 최종점수: {sum(final_score_values) / total_count:.2f}")

    print("\n손실 섹터 분석")

    for sector_name, returns in sector_stats.items():
        average_return = sum(returns) / len(returns)

        print(
            f"{sector_name} | "
            f"손실추천 {len(returns)}회 | "
            f"평균수익률 {average_return:.2f}%"
        )

    print("\n손실 시장상태 분석")

    for market_name, returns in market_stats.items():
        average_return = sum(returns) / len(returns)

        print(
            f"{market_name} | "
            f"손실추천 {len(returns)}회 | "
            f"평균수익률 {average_return:.2f}%"
        )

    connection.close()

def get_losing_recommendations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.rsi,
            r.atr_percent
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND p.current_return < 0
    """)

    rows = cursor.fetchall()
    connection.close()

    losing_recommendations = []

    for row in rows:
        losing_recommendations.append({
            "rsi": row[0],
            "atr_percent": row[1],
        })

    return losing_recommendations