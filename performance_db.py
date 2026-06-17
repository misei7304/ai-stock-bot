import yfinance as yf

from database import get_connection


def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="5d")

    if data.empty:
        return None

    return data["Close"].iloc[-1]


def calculate_return(recommended_price, current_price):
    return ((current_price - recommended_price) / recommended_price) * 100


def update_recommendation_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            recommendation_date,
            company_name,
            ticker,
            recommended_price
        FROM recommendations
    """)

    recommendations = cursor.fetchall()

    print("\n" + "#" * 80)
    print("DB 추천 수익률 업데이트")
    print("#" * 80)

    if len(recommendations) == 0:
        print("DB 추천 기록이 없습니다.")
        connection.close()
        return

    for recommendation in recommendations:
        (
            recommendation_id,
            recommendation_date,
            company_name,
            ticker,
            recommended_price,
        ) = recommendation

        current_price = get_current_price(ticker)

        if current_price is None:
            print(f"{company_name} | 현재가 데이터 없음")
            continue

        current_return = calculate_return(
            recommended_price,
            current_price
        )

        cursor.execute("""
            SELECT COUNT(*)
            FROM recommendation_performance
            WHERE recommendation_id = ?
        """, (
            recommendation_id,
        ))

        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            cursor.execute("""
                UPDATE recommendation_performance
                SET
                    current_price = ?,
                    current_return = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE recommendation_id = ?
            """, (
                current_price,
                current_return,
                recommendation_id,
            ))

        else:
            cursor.execute("""
                INSERT INTO recommendation_performance (
                    recommendation_id,
                    ticker,
                    company_name,
                    recommendation_date,
                    recommended_price,
                    current_price,
                    current_return,
                    return_1d,
                    return_5d,
                    return_20d
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL)
            """, (
                recommendation_id,
                ticker,
                company_name,
                recommendation_date,
                recommended_price,
                current_price,
                current_return,
            ))

        print(
            f"{recommendation_date} | "
            f"{company_name} | "
            f"{ticker} | "
            f"추천가 {recommended_price:,.0f}원 | "
            f"현재가 {current_price:,.0f}원 | "
            f"현재수익률 {current_return:.2f}%"
        )

    connection.commit()
    connection.close()

    print("DB 추천 수익률 업데이트 완료")