import numpy as np


FEATURES = [
    "Return",
    "MA5",
    "MA20",
    "MA60",
    "Volume_Change",
    "High_Low_Range",
    "Open_Close_Range",
    "MA5_Ratio",
    "MA20_Ratio",
    "MA60_Ratio",
    "Momentum_5",
    "Momentum_10",
]


def add_features(df):
    df = df.copy()

    df["Return"] = df["Close"].pct_change()
    df["MA5"] = df["Close"].rolling(window=5).mean()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA60"] = df["Close"].rolling(window=60).mean()
    df["Volume_Change"] = df["Volume"].pct_change()

    df["High_Low_Range"] = (df["High"] - df["Low"]) / df["Close"]
    df["Open_Close_Range"] = (df["Close"] - df["Open"]) / df["Open"]

    df["MA5_Ratio"] = df["Close"] / df["MA5"]
    df["MA20_Ratio"] = df["Close"] / df["MA20"]
    df["MA60_Ratio"] = df["Close"] / df["MA60"]

    df["Momentum_5"] = df["Close"] / df["Close"].shift(5) - 1
    df["Momentum_10"] = df["Close"] / df["Close"].shift(10) - 1

    df = df.replace([np.inf, -np.inf], np.nan)

    return df