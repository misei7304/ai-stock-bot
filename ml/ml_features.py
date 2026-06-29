import numpy as np


FEATURES = [
    "ATR_Percent",
    "MA60_Ratio",
    "MACD_Signal",
    "MACD",
    "ATR",
    "RSI",
    "High_Low_Range",
    "MA60",
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

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()

    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]

    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift(1)).abs()
    low_close = (df["Low"] - df["Close"].shift(1)).abs()

    true_range = np.maximum(high_low, np.maximum(high_close, low_close))

    df["ATR"] = true_range.rolling(window=14).mean()
    df["ATR_Percent"] = df["ATR"] / df["Close"] * 100

    df["Bollinger_Middle"] = df["Close"].rolling(window=20).mean()
    bollinger_std = df["Close"].rolling(window=20).std()

    df["Bollinger_Upper"] = df["Bollinger_Middle"] + (bollinger_std * 2)
    df["Bollinger_Lower"] = df["Bollinger_Middle"] - (bollinger_std * 2)

    df["Bollinger_Position"] = (
        (df["Close"] - df["Bollinger_Lower"]) /
        (df["Bollinger_Upper"] - df["Bollinger_Lower"])
    )

    df = df.replace([np.inf, -np.inf], np.nan)

    return df