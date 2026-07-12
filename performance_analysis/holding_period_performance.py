from storage.database import get_connection


def analyze_holding_period_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            return_1d,
            return_5d,
            return_20d
        FROM recommendation_performance
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("보유기간별 실전 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 보유기간 성과 데이터가 없습니다.")
        connection.close()
        return

    periods = {
        "1거래일": [],
        "5거래일": [],
        "20거래일": [],
    }

    for return_1d, return_5d, return_20d in rows:
        if return_1d is not None:
            periods["1거래일"].append(return_1d)

        if return_5d is not None:
            periods["5거래일"].append(return_5d)

        if return_20d is not None:
            periods["20거래일"].append(return_20d)

    for period_name, returns in periods.items():
        print(f"\n[{period_name}]")

        if len(returns) == 0:
            print("데이터 부족")
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