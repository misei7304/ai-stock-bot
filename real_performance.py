from database import get_connection


def analyze_real_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            current_return
        FROM recommendation_performance
        WHERE current_return IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("실전 추천 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 실전 추천 성과 데이터가 없습니다.")
        connection.close()
        return

    returns = []

    for row in rows:
        returns.append(row[0])

    total_count = len(returns)

    win_count = 0
    loss_count = 0

    for current_return in returns:
        if current_return > 0:
            win_count += 1
        else:
            loss_count += 1

    success_rate = (win_count / total_count) * 100
    average_return = sum(returns) / total_count

    best_return = max(returns)
    worst_return = min(returns)

    print(f"총 추천수: {total_count}회")
    print(f"수익중: {win_count}회")
    print(f"손실 또는 보합: {loss_count}회")
    print(f"성공률: {success_rate:.2f}%")
    print(f"평균수익률: {average_return:.2f}%")
    print(f"최고수익률: {best_return:.2f}%")
    print(f"최저수익률: {worst_return:.2f}%")

    connection.close()