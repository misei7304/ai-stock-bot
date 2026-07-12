from storage.database import get_connection


def check_real_risk_guard():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT current_return
        FROM recommendation_performance
        WHERE current_return IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("실전 리스크 경고")
    print("#" * 80)

    if len(rows) == 0:
        print("실전 데이터 부족: 실제 매수 금지, 관찰만 권장")
        connection.close()
        return False

    returns = [row[0] for row in rows]

    total_count = len(returns)
    win_count = 0

    for current_return in returns:
        if current_return > 0:
            win_count += 1

    success_rate = (win_count / total_count) * 100
    average_return = sum(returns) / total_count

    print(f"추천수: {total_count}회")
    print(f"성공률: {success_rate:.2f}%")
    print(f"평균수익률: {average_return:.2f}%")

    can_real_trade = False

    if total_count < 20:
        print("판단: 실전 데이터 부족")
        print("조치: 실제 매수 금지, 최소 20회 추천 기록까지 관찰만")
    elif average_return < 0:
        print("판단: 평균수익률 마이너스")
        print("조치: 실제 매수 금지, 전략 개선 필요")
    elif success_rate < 50:
        print("판단: 성공률 부족")
        print("조치: 실제 매수 금지, 조건 강화 필요")
    else:
        print("판단: 실전 매수 검토 가능")
        print("조치: 소액 테스트 가능")
        can_real_trade = True

    connection.close()

    return can_real_trade