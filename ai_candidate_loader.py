import os
import pandas as pd


def load_ai_candidates(path="ml/final_candidates.csv"):
    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)

    candidates = []

    for _, row in df.iterrows():
        candidates.append({
            "ticker": row["Ticker"],
            "ai_probability": float(row["Probability"]),
            "ai_close": float(row["Close"]),
            "ai_date": row["Date"],
        })

    return candidates


def is_ai_candidate(ticker, ai_candidates):
    return any(c["ticker"] == ticker for c in ai_candidates)


def get_ai_probability(ticker, ai_candidates):
    for c in ai_candidates:
        if c["ticker"] == ticker:
            return c["ai_probability"]
    return 0