from database import get_connection


def get_recommendation_type_performance_summary():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.recommendation_type,
            COUNT(*) AS recommendation_count,
            SUM(CASE WHEN p.current_return > 0 THEN 1 ELSE 0 END) AS win_count,
            AVG(p.current_return) AS average_return,
            MAX(p.current_return) AS best_return,
            MIN(p.current_return) AS worst_return
        FROM recommendations r
        JOIN recommendation_performance p
        ON r.id = p.recommendation_id
        WHERE p.current_return IS NOT NULL
        GROUP BY r.recommendation_type
        ORDER BY average_return DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    summary = []

    if len(rows) == 0:
        summary.append("추천 유형별 성과 데이터가 없습니다.")
        return summary

    for row in rows:
        recommendation_type, recommendation_count, win_count, average_return, best_return, worst_return = row

        if recommendation_type is None or recommendation_type == "":
            recommendation_type = "유형 없음"

        success_rate = win_count / recommendation_count * 100

        summary.append(f"[{recommendation_type}]")
        summary.append(f"추천수: {recommendation_count}회")
        summary.append(f"수익 추천수: {win_count}회")
        summary.append(f"성공률: {success_rate:.2f}%")
        summary.append(f"평균수익률: {average_return:.2f}%")
        summary.append(f"최고수익률: {best_return:.2f}%")
        summary.append(f"최저수익률: {worst_return:.2f}%")
        summary.append("")

    return summary


def analyze_recommendation_type_performance():
    print("\n" + "#" * 80)
    print("추천 유형별 성과 분석")
    print("#" * 80)

    summary = get_recommendation_type_performance_summary()

    for line in summary:
        print(line)