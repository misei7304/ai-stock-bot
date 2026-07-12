from datetime import datetime

from storage.history_performance_repository import (
    append_history_row,
    history_contains_recommendation,
)


HISTORY_FIELDNAMES = [
    "날짜",
    "종목명",
    "종목코드",
    "현재가",
    "최종점수",
    "RSI",
    "승률",
    "평균수익률",
    "현재수익률",
]


def build_history_row(
    best_stock,
    recommendation_date,
):
    return {
        "날짜": recommendation_date,
        "종목명": best_stock[
            "company_name"
        ],
        "종목코드": best_stock[
            "ticker"
        ],
        "현재가": round(
            best_stock[
                "current_price"
            ],
            0,
        ),
        "최종점수": round(
            best_stock[
                "final_score"
            ],
            2,
        ),
        "RSI": round(
            best_stock["rsi"],
            2,
        ),
        "승률": round(
            best_stock[
                "win_rate"
            ],
            2,
        ),
        "평균수익률": round(
            best_stock[
                "average_return"
            ],
            2,
        ),
        "현재수익률": 0,
    }


def save_history(
    best_stock,
):
    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    ticker = best_stock["ticker"]

    already_exists = (
        history_contains_recommendation(
            recommendation_date=today,
            ticker=ticker,
        )
    )

    if already_exists:
        print(
            "이미 오늘 추천 기록이 있습니다. "
            "히스토리 저장 생략"
        )
        return

    history_row = build_history_row(
        best_stock=best_stock,
        recommendation_date=today,
    )

    append_history_row(
        fieldnames=HISTORY_FIELDNAMES,
        row=history_row,
    )

    print("히스토리 저장 완료")