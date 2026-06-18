from database import get_connection


def analyze_sector_real_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.sector_name,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("섹터별 실전 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 섹터별 실전 성과 데이터가 없습니다.")
        connection.close()
        return

    sector_stats = {}

    for sector_name, current_return in rows:
        if sector_name not in sector_stats:
            sector_stats[sector_name] = []

        sector_stats[sector_name].append(current_return)

    sector_results = []

    for sector_name, returns in sector_stats.items():
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

        sector_results.append({
            "sector_name": sector_name,
            "total_count": total_count,
            "win_count": win_count,
            "loss_count": loss_count,
            "success_rate": success_rate,
            "average_return": average_return,
            "best_return": best_return,
            "worst_return": worst_return,
        })

    sector_results = sorted(
        sector_results,
        key=lambda x: x["average_return"],
        reverse=True
    )

    rank = 1

    for sector in sector_results:
        print(
            f"{rank}위 | "
            f"{sector['sector_name']} | "
            f"추천수 {sector['total_count']}회 | "
            f"수익중 {sector['win_count']}회 | "
            f"손실/보합 {sector['loss_count']}회 | "
            f"성공률 {sector['success_rate']:.2f}% | "
            f"평균수익률 {sector['average_return']:.2f}% | "
            f"최고수익률 {sector['best_return']:.2f}% | "
            f"최저수익률 {sector['worst_return']:.2f}%"
        )

        rank += 1

    connection.close()