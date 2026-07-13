import os
from datetime import date, datetime

import pandas as pd


MAX_AI_CANDIDATE_AGE_BUSINESS_DAYS = 1


def parse_ai_date(value):
    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    parsed_date = pd.to_datetime(
        value,
        errors="coerce",
    )

    if pd.isna(parsed_date):
        return None

    return parsed_date.date()


def calculate_business_day_age(
    candidate_date,
    reference_date=None,
):
    if reference_date is None:
        reference_date = date.today()

    if candidate_date >= reference_date:
        return 0

    business_days = pd.bdate_range(
        start=candidate_date,
        end=reference_date,
    )

    return max(
        len(business_days) - 1,
        0,
    )


def is_ai_candidate_fresh(
    candidate_date,
    reference_date=None,
):
    parsed_date = parse_ai_date(
        candidate_date
    )

    if parsed_date is None:
        return False

    age = calculate_business_day_age(
        candidate_date=parsed_date,
        reference_date=reference_date,
    )

    return (
        age
        <= MAX_AI_CANDIDATE_AGE_BUSINESS_DAYS
    )


def load_ai_candidates(
    path="ml/final_candidates.csv",
):
    if not os.path.exists(path):
        print(
            f"AI 후보 파일이 없습니다: {path}"
        )
        return []

    df = pd.read_csv(path)

    required_columns = {
        "Ticker",
        "Probability",
        "Close",
        "Date",
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "AI 후보 CSV 필수 컬럼이 없습니다: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    candidates = []

    for _, row in df.iterrows():
        ticker = str(
            row["Ticker"]
        ).strip()

        ai_date = row["Date"]

        if not ticker:
            continue

        if not is_ai_candidate_fresh(
            ai_date
        ):
            print(
                "오래된 AI 후보 제외: "
                f"{ticker} | "
                f"기준일 {ai_date}"
            )
            continue

        try:
            ai_probability = float(
                row["Probability"]
            )

            ai_close = float(
                row["Close"]
            )

        except (TypeError, ValueError):
            print(
                "잘못된 AI 후보 제외: "
                f"{ticker} | "
                "확률 또는 종가 변환 실패"
            )
            continue

        candidates.append({
            "ticker": ticker,
            "ai_probability": (
                ai_probability
            ),
            "ai_close": ai_close,
            "ai_date": str(ai_date),
        })

    return candidates


def is_ai_candidate(
    ticker,
    ai_candidates,
):
    return any(
        candidate["ticker"] == ticker
        for candidate in ai_candidates
    )


def get_ai_probability(
    ticker,
    ai_candidates,
):
    for candidate in ai_candidates:
        if candidate["ticker"] == ticker:
            return candidate[
                "ai_probability"
            ]

    return 0

def convert_scan_results_to_ai_candidates(
    scan_results,
):
    candidates = []

    for result in scan_results:
        ticker = str(
            result.get("Ticker") or ""
        ).strip()

        ai_date = result.get("Date")

        if not ticker:
            continue

        if not is_ai_candidate_fresh(
            ai_date
        ):
            print(
                "오래된 AI 스캔 결과 제외: "
                f"{ticker} | "
                f"기준일 {ai_date}"
            )
            continue

        try:
            ai_probability = float(
                result.get("Probability")
            )

            ai_close = float(
                result.get("Close")
            )

        except (TypeError, ValueError):
            print(
                "잘못된 AI 스캔 결과 제외: "
                f"{ticker}"
            )
            continue

        candidates.append({
            "ticker": ticker,
            "ai_probability": (
                ai_probability
            ),
            "ai_close": ai_close,
            "ai_date": str(ai_date),
        })

    return candidates