import pandas as pd

from market_data.data import (
    get_stock_data,
)
from storage.history_performance_repository import (
    history_file_exists,
    load_history_rows,
    save_history_rows,
)


PERFORMANCE_PERIODS = {
    "1거래일": 1,
    "5거래일": 5,
    "20거래일": 20,
}


def calculate_return(
    target_price,
    recommended_price,
):
    return (
        (
            target_price
            - recommended_price
        )
        / recommended_price
    ) * 100


def normalize_stock_data(
    data,
):
    data = data.dropna(
        subset=["Close"]
    )

    if data.empty:
        return data

    data = data.reset_index()

    data["Date"] = (
        pd.to_datetime(
            data["Date"]
        )
        .dt
        .tz_localize(None)
        .dt
        .date
    )

    return data


def get_after_recommendation_data(
    data,
    recommendation_date,
):
    return data[
        data["Date"]
        >= recommendation_date
    ].reset_index(drop=True)


def calculate_period_return(
    after_recommendation,
    recommended_price,
    period,
):
    target_index = period

    if (
        target_index
        >= len(after_recommendation)
    ):
        return None

    target_price = (
        after_recommendation[
            "Close"
        ].iloc[target_index]
    )

    if pd.isna(target_price):
        return None

    return calculate_return(
        target_price=target_price,
        recommended_price=recommended_price,
    )


def print_period_returns(
    after_recommendation,
    recommended_price,
):
    for period_name, period in (
        PERFORMANCE_PERIODS.items()
    ):
        period_return = (
            calculate_period_return(
                after_recommendation=(
                    after_recommendation
                ),
                recommended_price=(
                    recommended_price
                ),
                period=period,
            )
        )

        if period_return is None:
            print(
                f"  {period_name} 후 "
                "수익률: 데이터 부족"
            )
            continue

        print(
            f"  {period_name} 후 "
            f"수익률: "
            f"{period_return:.2f}%"
        )


def update_single_history_row(
    row,
):
    recommendation_date = (
        pd.to_datetime(
            row["날짜"]
        ).date()
    )

    company_name = row["종목명"]
    ticker = row["종목코드"]

    recommended_price = float(
        row["현재가"]
    )

    data = get_stock_data(
        ticker,
        period="1y",
    )

    data = normalize_stock_data(
        data
    )

    if data.empty:
        print(
            f"{row['날짜']} | "
            f"{company_name} | "
            "가격 데이터 없음"
        )
        return row

    after_recommendation = (
        get_after_recommendation_data(
            data=data,
            recommendation_date=(
                recommendation_date
            ),
        )
    )

    if after_recommendation.empty:
        print(
            f"{row['날짜']} | "
            f"{company_name} | "
            "추천 이후 데이터 없음"
        )
        return row

    current_price = (
        after_recommendation[
            "Close"
        ].iloc[-1]
    )

    if pd.isna(current_price):
        print(
            f"{row['날짜']} | "
            f"{company_name} | "
            "현재가 데이터 없음"
        )
        return row

    current_return = calculate_return(
        target_price=current_price,
        recommended_price=(
            recommended_price
        ),
    )

    row["현재수익률"] = round(
        current_return,
        2,
    )

    print(
        f"{row['날짜']} | "
        f"{company_name} | "
        f"추천가 "
        f"{recommended_price:,.0f}원 | "
        f"현재가 "
        f"{current_price:,.0f}원 | "
        f"현재수익률 "
        f"{current_return:.2f}%"
    )

    print_period_returns(
        after_recommendation=(
            after_recommendation
        ),
        recommended_price=(
            recommended_price
        ),
    )

    return row


def analyze_recommendation_performance():
    if not history_file_exists():
        print(
            "history.csv 파일이 없습니다."
        )
        return

    print("\n" + "#" * 80)
    print("추천 후 수익률 추적")
    print("#" * 80)

    history_data = load_history_rows()

    fieldnames = history_data[
        "fieldnames"
    ]

    rows = history_data["rows"]

    if "현재수익률" not in fieldnames:
        fieldnames.append(
            "현재수익률"
        )

    updated_rows = []

    for row in rows:
        updated_row = (
            update_single_history_row(
                row
            )
        )

        updated_rows.append(
            updated_row
        )

    save_history_rows(
        fieldnames=fieldnames,
        rows=updated_rows,
    )

    print(
        "\n현재수익률 업데이트 완료"
    )