import csv
import os
import pandas as pd


def analyze_strategy_performance():

    if not os.path.exists("history.csv"):
        print("history.csv 파일이 없습니다.")
        return

    print("\n" + "#" * 80)
    print("전략 성과 분석")
    print("#" * 80)

    recommendation_count = 0
    stock_stats = {}

    with open(
        "history.csv",
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            recommendation_count += 1

            company_name = row["종목명"]
            current_return_text = row.get("현재수익률", "")

            if current_return_text == "":
                continue

            current_return = float(current_return_text)

            if pd.isna(current_return):
                continue

            if company_name not in stock_stats:
                stock_stats[company_name] = {
                    "count": 0,
                    "total_return": 0,
                    "success_count": 0,
                }

            stock_stats[company_name]["count"] += 1
            stock_stats[company_name]["total_return"] += current_return

            if current_return > 0:
                stock_stats[company_name]["success_count"] += 1

    print(f"총 추천 횟수: {recommendation_count}")

    print("\n추천 종목별 성과")

    ranking = []

    for company_name, stats in stock_stats.items():

        count = stats["count"]
        average_return = stats["total_return"] / count
        success_rate = (stats["success_count"] / count) * 100

        ranking.append({
            "company_name": company_name,
            "count": count,
            "average_return": average_return,
            "success_rate": success_rate,
        })

    ranking = sorted(
        ranking,
        key=lambda x: x["average_return"],
        reverse=True
    )

    print("\n종목별 성과 랭킹")

    if len(ranking) == 0:
        print("분석 가능한 전략 성과 데이터가 없습니다.")
        return

    rank = 1

    for stock in ranking:

        print(f"\n{rank}위 {stock['company_name']}")
        print(f"추천횟수: {stock['count']}회")
        print(f"평균수익률: {stock['average_return']:.2f}%")
        print(f"성공률: {stock['success_rate']:.2f}%")

        rank += 1