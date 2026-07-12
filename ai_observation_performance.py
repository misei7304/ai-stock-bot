import pandas as pd
import yfinance as yf

from storage.ai_observation_performance_database import (
    ensure_ai_performance_columns,
    get_ai_observations,
    update_ai_observation_returns,
)


def normalize_stock_data(data):
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data.dropna()


def calculate_return(
    target_close,
    base_close,
):
    return (
        (target_close / base_close) - 1
    ) * 100


def calculate_period_returns(
    data,
    base_index,
    ai_close,
):
    period_returns = {
        "return_1d": None,
        "return_5d": None,
        "return_20d": None,
    }

    periods = {
        "return_1d": 1,
        "return_5d": 5,
        "return_20d": 20,
    }

    for return_name, period in periods.items():
        target_index = base_index + period

        if target_index >= len(data):
            continue

        target_close = float(
            data["Close"].iloc[target_index]
        )

        period_returns[return_name] = (
            calculate_return(
                target_close,
                ai_close,
            )
        )

    return period_returns


def update_single_ai_observation(
    observation,
):
    observation_id = observation["id"]
    ticker = observation["ticker"]
    ai_date = observation["ai_date"]
    ai_close = observation["ai_close"]

    data = yf.download(
        ticker,
        period="2mo",
        progress=False,
    )

    if data.empty:
        return False

    data = normalize_stock_data(data)

    date_list = list(
        data.index.strftime("%Y-%m-%d")
    )

    if ai_date not in date_list:
        return False

    base_index = date_list.index(ai_date)

    current_close = float(
        data["Close"].iloc[-1]
    )

    current_return = calculate_return(
        current_close,
        ai_close,
    )

    period_returns = calculate_period_returns(
        data=data,
        base_index=base_index,
        ai_close=ai_close,
    )

    update_ai_observation_returns(
        observation_id=observation_id,
        current_close=current_close,
        current_return=current_return,
        return_1d=period_returns["return_1d"],
        return_5d=period_returns["return_5d"],
        return_20d=period_returns["return_20d"],
    )

    print(
        f"{ai_date} | {ticker} | "
        f"AI추천가 {ai_close:,.0f}원 | "
        f"현재가 {current_close:,.0f}원 | "
        f"현재수익률 {current_return:.2f}%"
    )

    return True


def update_ai_observation_performance():
    ensure_ai_performance_columns()

    observations = get_ai_observations()

    for observation in observations:
        update_single_ai_observation(
            observation
        )

    print("AI 후보 수익률 업데이트 완료")