import csv
import os
import pandas as pd

from data import get_stock_data


def calculate_return(target_price, recommended_price):
    return ((target_price - recommended_price) / recommended_price) * 100


def analyze_recommendation_performance():

    file_name = "history.csv"

    if not os.path.exists(file_name):
        print("history.csv 파일이 없습니다.")
        return

    print("\n" + "#" * 80)
    print("추천 후 수익률 추적")
    print("#" * 80)

    updated_rows = []

    with open(
        file_name,
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames

        if "현재수익률" not in fieldnames:
            fieldnames.append("현재수익률")

        for row in reader:
            recommendation_date = pd.to_datetime(row["날짜"])
            company_name = row["종목명"]
            ticker = row["종목코드"]
            recommended_price = float(row["현재가"])

            data = get_stock_data(ticker, period="1y")

            data = data.reset_index()
            data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize(None)

            after_recommendation = data[
                data["Date"] >= recommendation_date
            ].reset_index(drop=True)

            if len(after_recommendation) == 0:
                print(f"{row['날짜']} | {company_name} | 추천 이후 데이터 없음")
                updated_rows.append(row)
                continue

            current_price = after_recommendation["Close"].iloc[-1]
            current_return = calculate_return(
                current_price,
                recommended_price
            )

            row["현재수익률"] = round(current_return, 2)

            print(
                f"{row['날짜']} | "
                f"{company_name} | "
                f"추천가 {recommended_price:,.0f}원 | "
                f"현재가 {current_price:,.0f}원 | "
                f"현재수익률 {current_return:.2f}%"
            )

            if len(after_recommendation) >= 2:
                one_day_price = after_recommendation["Close"].iloc[1]
                one_day_return = calculate_return(
                    one_day_price,
                    recommended_price
                )
                print(f"  1거래일 후 수익률: {one_day_return:.2f}%")
            else:
                print("  1거래일 후 수익률: 데이터 부족")

            if len(after_recommendation) >= 6:
                five_day_price = after_recommendation["Close"].iloc[5]
                five_day_return = calculate_return(
                    five_day_price,
                    recommended_price
                )
                print(f"  5거래일 후 수익률: {five_day_return:.2f}%")
            else:
                print("  5거래일 후 수익률: 데이터 부족")

            if len(after_recommendation) >= 21:
                twenty_day_price = after_recommendation["Close"].iloc[20]
                twenty_day_return = calculate_return(
                    twenty_day_price,
                    recommended_price
                )
                print(f"  20거래일 후 수익률: {twenty_day_return:.2f}%")
            else:
                print("  20거래일 후 수익률: 데이터 부족")

            updated_rows.append(row)

    with open(
        file_name,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(updated_rows)

    print("\n현재수익률 업데이트 완료")