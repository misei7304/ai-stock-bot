from storage.stock_report_repository import (
    save_stock_report_rows,
)


STOCK_REPORT_FIELDNAMES = [
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
    "ATR",
    "ATR_PERCENT",
    "ATR_SCORE",
    "승률",
    "평균수익률",
    "최종자산",
    "매수후보",
]


def build_stock_report_row(
    stock,
):
    return {
        "종목명": stock[
            "company_name"
        ],
        "종목코드": stock[
            "ticker"
        ],
        "현재점수": round(
            stock["total_score"],
            2,
        ),
        "최종점수": round(
            stock["final_score"],
            2,
        ),
        "RSI": round(
            stock["rsi"],
            2,
        ),
        "MACD": round(
            stock["macd"],
            2,
        ),
        "MACD_SIGNAL": round(
            stock["macd_signal"],
            2,
        ),
        "MACD_HISTOGRAM": round(
            stock["macd_histogram"],
            2,
        ),
        "BOLLINGER_UPPER": round(
            stock["bollinger_upper"],
            0,
        ),
        "BOLLINGER_MIDDLE": round(
            stock["bollinger_middle"],
            0,
        ),
        "BOLLINGER_LOWER": round(
            stock["bollinger_lower"],
            0,
        ),
        "BOLLINGER_SCORE": stock[
            "bollinger_score"
        ],
        "ATR": round(
            stock["atr"],
            0,
        ),
        "ATR_PERCENT": round(
            stock["atr_percent"],
            2,
        ),
        "ATR_SCORE": stock[
            "atr_score"
        ],
        "승률": round(
            stock["win_rate"],
            2,
        ),
        "평균수익률": round(
            stock["average_return"],
            2,
        ),
        "최종자산": round(
            stock["final_money"],
            0,
        ),
        "매수후보": stock[
            "is_buy_candidate"
        ],
    }


def build_stock_report_rows(
    results,
):
    rows = []

    for stock in results:
        rows.append(
            build_stock_report_row(
                stock
            )
        )

    return rows


def save_report(
    results,
):
    rows = build_stock_report_rows(
        results
    )

    save_stock_report_rows(
        fieldnames=(
            STOCK_REPORT_FIELDNAMES
        ),
        rows=rows,
    )

    print("\nCSV 저장 완료")