import csv
import os

from data import get_stock_data


def analyze_recommendation_performance():

    if not os.path.exists("history.csv"):
        print("history.csv 파일이 없습니다.")
        return

    print("\n" + "#" * 80)
    print("추천 후 수익률 추적")
    print("#" * 80)

    with open(
        "history.csv",
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            date = row["날짜"]
            company_name = row["종목명"]
            ticker = row["종목코드"]
            recommended_price = float(row["현재가"])

            data = get_stock_data(ticker, period="5d")
            current_price = data["Close"].iloc[-1]

            profit_rate = (
                (current_price - recommended_price)
                / recommended_price
            ) * 100

            print(
                f"{date} | "
                f"{company_name} | "
                f"추천가 {recommended_price:,.0f}원 | "
                f"현재가 {current_price:,.0f}원 | "
                f"추천 후 수익률 {profit_rate:.2f}%"
            )