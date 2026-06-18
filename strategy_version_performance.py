from database import get_connection


def analyze_strategy_version_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.strategy_version,
            COUNT(*) AS recommendation_count,
            SUM(CASE WHEN p.current_return > 0 THEN 1 ELSE 0 END) AS win_count,
            AVG(p.current_return) AS average_return,
            MAX(p.current_return) AS best_return,
            MIN(p.current_return) AS worst_return
        FROM recommendations r
        JOIN recommendation_performance p
        ON r.id = p.recommendation_id
        WHERE p.current_return IS NOT NULL
        GROUP BY r.strategy_version
        ORDER BY average_return DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    print("\n" + "#" * 80)
    print("전략 버전별 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("전략 버전별 성과 데이터가 없습니다.")
        return

    best_version = None
    best_average_return = None

    for row in rows:
        (
            strategy_version,
            recommendation_count,
            win_count,
            average_return,
            best_return,
            worst_return,
        ) = row

        if strategy_version is None or strategy_version == "":
            strategy_version = "버전 없음"

        success_rate = win_count / recommendation_count * 100

        print(f"\n전략 버전: {strategy_version}")
        print(f"추천수: {recommendation_count}회")
        print(f"수익 추천수: {win_count}회")
        print(f"성공률: {success_rate:.2f}%")
        print(f"평균수익률: {average_return:.2f}%")
        print(f"최고수익률: {best_return:.2f}%")
        print(f"최저수익률: {worst_return:.2f}%")

        if best_average_return is None or average_return > best_average_return:
            best_average_return = average_return
            best_version = strategy_version

    print("\n최고 전략 버전")
    print(f"전략 버전: {best_version}")
    print(f"평균수익률: {best_average_return:.2f}%")