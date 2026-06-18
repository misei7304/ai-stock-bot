from database import get_connection


def analyze_recommendation_reason_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.recommendation_reason,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND r.recommendation_reason IS NOT NULL
    """)

    rows = cursor.fetchall()
    connection.close()

    print("\n" + "#" * 80)
    print("추천 이유별 실전 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 추천 이유 데이터가 없습니다.")
        return

    reason_stats = {}

    for recommendation_reason, current_return in rows:
        reasons = recommendation_reason.split(". ")

        for reason in reasons:
            reason = reason.strip()

            if reason == "":
                continue

            if reason not in reason_stats:
                reason_stats[reason] = []

            reason_stats[reason].append(current_return)

    reason_results = []

    for reason, returns in reason_stats.items():
        total_count = len(returns)
        average_return = sum(returns) / total_count
        win_count = sum(1 for current_return in returns if current_return > 0)
        success_rate = (win_count / total_count) * 100

        reason_results.append({
            "reason": reason,
            "total_count": total_count,
            "average_return": average_return,
            "success_rate": success_rate,
        })

    reason_results = sorted(
        reason_results,
        key=lambda x: x["average_return"],
        reverse=True
    )

    for result in reason_results:
        print(
            f"{result['reason']} | "
            f"추천수 {result['total_count']}회 | "
            f"평균수익률 {result['average_return']:.2f}% | "
            f"성공률 {result['success_rate']:.2f}%"
        )