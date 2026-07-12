import pandas as pd
import yfinance as yf

from storage.database import get_connection


def get_price_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1y")

    data = data.dropna(subset=["Close"])

    if data.empty:
        return None

    data = data.reset_index()
    data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize(None).dt.date

    return data


def calculate_return(recommended_price, target_price):
    return ((target_price - recommended_price) / recommended_price) * 100


def get_return_after_days(data, recommendation_date, recommended_price, days):
    after_recommendation = data[
        data["Date"] >= recommendation_date
    ].reset_index(drop=True)

    if len(after_recommendation) <= days:
        return None

    target_price = after_recommendation["Close"].iloc[days]

    if pd.isna(target_price):
        return None

    return calculate_return(recommended_price, target_price)


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

        recommendation_date = pd.to_datetime(recommendation_date).date()

        data = get_price_data(ticker)

        if data is None:
            print(f"{company_name} | 가격 데이터 없음")
            continue

        after_recommendation = data[
            data["Date"] >= recommendation_date
        ].reset_index(drop=True)

        if len(after_recommendation) == 0:
            print(f"{company_name} | 추천 이후 가격 데이터 없음")
            continue

        current_price = after_recommendation["Close"].iloc[-1]

        if pd.isna(current_price):
            print(f"{company_name} | 현재가 데이터 없음")
            continue

        current_return = calculate_return(
            recommended_price,
            current_price
        )

        return_1d = get_return_after_days(
            data,
            recommendation_date,
            recommended_price,
            1
        )

        return_5d = get_return_after_days(
            data,
            recommendation_date,
            recommended_price,
            5
        )

        return_20d = get_return_after_days(
            data,
            recommendation_date,
            recommended_price,
            20
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
                    return_1d = ?,
                    return_5d = ?,
                    return_20d = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE recommendation_id = ?
            """, (
                current_price,
                current_return,
                return_1d,
                return_5d,
                return_20d,
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recommendation_id,
                ticker,
                company_name,
                recommendation_date,
                recommended_price,
                current_price,
                current_return,
                return_1d,
                return_5d,
                return_20d,
            ))

        print(
            f"{recommendation_date} | "
            f"{company_name} | "
            f"{ticker} | "
            f"추천가 {recommended_price:,.0f}원 | "
            f"현재가 {current_price:,.0f}원 | "
            f"현재수익률 {current_return:.2f}%"
        )

        if return_1d is None:
            print("  1거래일 후 수익률: 데이터 부족")
        else:
            print(f"  1거래일 후 수익률: {return_1d:.2f}%")

        if return_5d is None:
            print("  5거래일 후 수익률: 데이터 부족")
        else:
            print(f"  5거래일 후 수익률: {return_5d:.2f}%")

        if return_20d is None:
            print("  20거래일 후 수익률: 데이터 부족")
        else:
            print(f"  20거래일 후 수익률: {return_20d:.2f}%")

    connection.commit()
    connection.close()

    print("DB 추천 수익률 업데이트 완료")