from storage.database import get_connection


def analyze_strategy_score():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT current_return
        FROM recommendation_performance
        WHERE current_return IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("실전 전략 점수")
    print("#" * 80)

    if len(rows) == 0:
        print("실전 데이터 부족")
        connection.close()
        return

    returns = [row[0] for row in rows]

    recommendation_count = len(returns)

    win_count = 0

    for current_return in returns:
        if current_return > 0:
            win_count += 1

    success_rate = (win_count / recommendation_count) * 100
    average_return = sum(returns) / recommendation_count

    strategy_score = (
        success_rate * 0.7
        + average_return * 3
    )

    print(f"추천수: {recommendation_count}회")
    print(f"성공률: {success_rate:.2f}%")
    print(f"평균수익률: {average_return:.2f}%")
    print(f"전략점수: {strategy_score:.2f}")

    if strategy_score >= 70:
        print("평가: 매우 우수")
    elif strategy_score >= 50:
        print("평가: 우수")
    elif strategy_score >= 30:
        print("평가: 보통")
    else:
        print("평가: 개선 필요")

    connection.close()