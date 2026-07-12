from storage.database import get_connection


def analyze_market_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.market_bull,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("시장 상태별 실전 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 시장 상태별 성과 데이터가 없습니다.")
        connection.close()
        return

    market_stats = {
        1: [],
        0: [],
    }

    for market_bull, current_return in rows:
        market_stats[market_bull].append(current_return)

    for market_bull, returns in market_stats.items():
        market_name = "상승장" if market_bull == 1 else "약세장"

        print(f"\n[{market_name}]")

        if len(returns) == 0:
            print("추천 기록 없음")
            continue

        total_count = len(returns)
        win_count = 0

        for current_return in returns:
            if current_return > 0:
                win_count += 1

        loss_count = total_count - win_count
        success_rate = (win_count / total_count) * 100
        average_return = sum(returns) / total_count
        best_return = max(returns)
        worst_return = min(returns)

        print(f"추천수: {total_count}회")
        print(f"수익중: {win_count}회")
        print(f"손실 또는 보합: {loss_count}회")
        print(f"성공률: {success_rate:.2f}%")
        print(f"평균수익률: {average_return:.2f}%")
        print(f"최고수익률: {best_return:.2f}%")
        print(f"최저수익률: {worst_return:.2f}%")

    connection.close()