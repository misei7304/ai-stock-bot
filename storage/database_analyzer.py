import sqlite3


DATABASE_NAME = "stock_bot.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def analyze_database_recommendations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM recommendations
    """)

    total_count = cursor.fetchone()[0]

    print("\n" + "#" * 80)
    print("DB 추천 기록 분석")
    print("#" * 80)

    if total_count == 0:
        print("DB에 저장된 추천 기록이 없습니다.")
        connection.close()
        return

    print(f"총 DB 추천 기록 수: {total_count}회")

    cursor.execute("""
        SELECT
            company_name,
            ticker,
            COUNT(*) AS recommendation_count,
            AVG(final_score) AS average_final_score,
            AVG(current_score) AS average_current_score,
            AVG(win_rate) AS average_win_rate,
            AVG(average_return) AS average_return,
            AVG(final_money) AS average_final_money
        FROM recommendations
        GROUP BY company_name, ticker
        ORDER BY recommendation_count DESC, average_final_score DESC
    """)

    rows = cursor.fetchall()

    print("\n종목별 DB 추천 기록")

    rank = 1

    for row in rows:
        (
            company_name,
            ticker,
            recommendation_count,
            average_final_score,
            average_current_score,
            average_win_rate,
            average_return,
            average_final_money,
        ) = row

        print(
            f"{rank}위 | "
            f"{company_name} | "
            f"{ticker} | "
            f"추천횟수 {recommendation_count}회 | "
            f"평균최종점수 {average_final_score:.2f} | "
            f"평균현재점수 {average_current_score:.2f} | "
            f"평균승률 {average_win_rate:.2f}% | "
            f"평균수익 {average_return:.2f}% | "
            f"평균최종자산 {average_final_money:,.0f}원"
        )

        rank += 1

    cursor.execute("""
        SELECT
            recommendation_date,
            company_name,
            ticker,
            recommended_price,
            final_score,
            current_score,
            win_rate,
            average_return,
            quantity,
            investment_amount,
            created_at
        FROM recommendations
        ORDER BY id DESC
        LIMIT 10
    """)

    recent_rows = cursor.fetchall()

    print("\n최근 DB 추천 기록 10개")

    for row in recent_rows:
        (
            recommendation_date,
            company_name,
            ticker,
            recommended_price,
            final_score,
            current_score,
            win_rate,
            average_return,
            quantity,
            investment_amount,
            created_at,
        ) = row

        print(
            f"{recommendation_date} | "
            f"{company_name} | "
            f"{ticker} | "
            f"추천가 {recommended_price:,.0f}원 | "
            f"최종점수 {final_score:.2f} | "
            f"현재점수 {current_score:.2f} | "
            f"승률 {win_rate:.2f}% | "
            f"평균수익 {average_return:.2f}% | "
            f"{quantity}주 | "
            f"투자금액 {investment_amount:,.0f}원 | "
            f"저장시각 {created_at}"
        )

    connection.close()