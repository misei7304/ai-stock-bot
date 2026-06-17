import csv
import os


def analyze_history():
    if not os.path.exists("history.csv"):
        print("history.csv 파일이 없습니다.")
        return

    recommendation_count = {}

    with open(
        "history.csv",
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            company_name = row["종목명"]

            if company_name not in recommendation_count:
                recommendation_count[company_name] = 0

            recommendation_count[company_name] += 1

    print("\n" + "#" * 80)
    print("추천 히스토리 요약")
    print("#" * 80)

    sorted_history = sorted(
        recommendation_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for company_name, count in sorted_history:
        print(f"{company_name}: {count}회 추천")