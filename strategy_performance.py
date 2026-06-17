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
            current_return = float(row.get("현재수익률", 0))

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

    sorted_stats = sorted(
        stock_stats.items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )

    for company_name, stats in sorted_stats:

        count = stats["count"]
        average_return = stats["total_return"] / count
        success_rate = (stats["success_count"] / count) * 100

        print(f"\n{company_name}")
        print(f"추천횟수: {count}회")
        print(f"평균수익률: {average_return:.2f}%")
        print(f"성공률: {success_rate:.2f}%")