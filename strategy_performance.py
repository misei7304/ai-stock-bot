import csv
import os


def analyze_strategy_performance():

    if not os.path.exists("history.csv"):
        print("history.csv 파일이 없습니다.")
        return

    print("\n" + "#" * 80)
    print("전략 성과 분석")
    print("#" * 80)

    recommendation_count = 0
    stock_counts = {}

    with open(
        "history.csv",
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            recommendation_count += 1

            company_name = row["종목명"]

            if company_name not in stock_counts:
                stock_counts[company_name] = 0

            stock_counts[company_name] += 1

    print(f"총 추천 횟수: {recommendation_count}")

    print("\n추천 종목별 횟수")

    for company_name, count in sorted(
        stock_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"{company_name}: {count}회")