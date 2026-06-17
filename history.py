import csv
import os
from datetime import datetime


def save_history(best_stock):

    file_name = "history.csv"
    today = datetime.now().strftime("%Y-%m-%d")

    file_exists = os.path.exists(file_name)

    if file_exists:
        with open(
            file_name,
            "r",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                same_date = row["날짜"] == today
                same_ticker = row["종목코드"] == best_stock["ticker"]

                if same_date and same_ticker:
                    print("이미 오늘 추천 기록이 있습니다. 히스토리 저장 생략")
                    return

    with open(
        file_name,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "날짜",
                "종목명",
                "종목코드",
                "현재가",
                "최종점수",
                "RSI",
                "승률",
                "평균수익률",
                "현재수익률"
            ])

        writer.writerow([
            today,
            best_stock["company_name"],
            best_stock["ticker"],
            round(best_stock["current_price"], 0),
            round(best_stock["final_score"], 2),
            round(best_stock["rsi"], 2),
            round(best_stock["win_rate"], 2),
            round(best_stock["average_return"], 2),
            0
        ])

    print("히스토리 저장 완료")