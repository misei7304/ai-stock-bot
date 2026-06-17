import csv


def save_report(results):

    with open(
        "stock_report.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "종목명",
            "종목코드",
            "현재점수",
            "최종점수",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
            "MACD_HISTOGRAM",
            "BOLLINGER_UPPER",
            "BOLLINGER_MIDDLE",
            "BOLLINGER_LOWER",
            "BOLLINGER_SCORE",
            "승률",
            "평균수익률",
            "최종자산",
            "매수후보"
        ])

        for stock in results:

            writer.writerow([
                stock["company_name"],
                stock["ticker"],
                round(stock["total_score"], 2),
                round(stock["final_score"], 2),
                round(stock["rsi"], 2),
                round(stock["macd"], 2),
                round(stock["macd_signal"], 2),
                round(stock["macd_histogram"], 2),
                round(stock["bollinger_upper"], 0),
                round(stock["bollinger_middle"], 0),
                round(stock["bollinger_lower"], 0),
                stock["bollinger_score"],
                round(stock["win_rate"], 2),
                round(stock["average_return"], 2),
                round(stock["final_money"], 0),
                stock["is_buy_candidate"]
            ])

    print("\nCSV 저장 완료")