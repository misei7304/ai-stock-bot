import numpy as np


BASE_FEATURES = [
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


NEW_FEATURES = [
    "MA120_Ratio",
    "Volume_Ratio_20",
    "Turnover_Ratio_20",
    "Distance_From_20D_High",
    "Volatility_20",
    "OBV_Imbalance_20",
]


ALL_FEATURES = (
    BASE_FEATURES
    + NEW_FEATURES
)


# 현재 실전 모델은 아직 기존 10개 Feature 사용
# 검증 완료 전까지 변경하지 않는다.
FEATURES = BASE_FEATURES


def add_features(df):
    df = df.copy()

    df["Return"] = (
        df["Close"].pct_change()
    )

    df["MA5"] = (
        df["Close"]
        .rolling(window=5)
        .mean()
    )

    df["MA20"] = (
        df["Close"]
        .rolling(window=20)
        .mean()
    )

    df["MA60"] = (
        df["Close"]
        .rolling(window=60)
        .mean()
    )

    df["MA120"] = (
        df["Close"]
        .rolling(window=120)
        .mean()
    )

    df["Volume_Change"] = (
        df["Volume"].pct_change()
    )

    df["High_Low_Range"] = (
        (df["High"] - df["Low"])
        / df["Close"]
    )

    df["Open_Close_Range"] = (
        (df["Close"] - df["Open"])
        / df["Open"]
    )

    df["MA5_Ratio"] = (
        df["Close"] / df["MA5"]
    )

    df["MA20_Ratio"] = (
        df["Close"] / df["MA20"]
    )

    df["MA60_Ratio"] = (
        df["Close"] / df["MA60"]
    )

    df["MA120_Ratio"] = (
        df["Close"] / df["MA120"]
    )

    df["Momentum_5"] = (
        df["Close"]
        / df["Close"].shift(5)
        - 1
    )

    df["Momentum_10"] = (
        df["Close"]
        / df["Close"].shift(10)
        - 1
    )

    volume_ma20 = (
        df["Volume"]
        .rolling(window=20)
        .mean()
    )

    df["Volume_Ratio_20"] = (
        df["Volume"] / volume_ma20
    )

    df["Turnover"] = (
        df["Close"] * df["Volume"]
    )

    turnover_ma20 = (
        df["Turnover"]
        .rolling(window=20)
        .mean()
    )

    df["Turnover_Ratio_20"] = (
        df["Turnover"]
        / turnover_ma20
    )

    high_20 = (
        df["Close"]
        .rolling(window=20)
        .max()
    )

    df["Distance_From_20D_High"] = (
        df["Close"] / high_20 - 1
    )

    df["Volatility_20"] = (
        df["Return"]
        .rolling(window=20)
        .std()
    )

    price_direction = np.sign(
        df["Close"].diff()
    ).fillna(0)

    df["OBV"] = (
        price_direction
        * df["Volume"]
    ).cumsum()

    rolling_volume_20 = (
        df["Volume"]
        .rolling(window=20)
        .sum()
    )

    df["OBV_Imbalance_20"] = (
        (
            df["OBV"]
            - df["OBV"].shift(20)
        )
        / rolling_volume_20
    )

    delta = df["Close"].diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    avg_gain = (
        gain
        .rolling(window=14)
        .mean()
    )

    avg_loss = (
        loss
        .rolling(window=14)
        .mean()
    )

    rs = avg_gain / avg_loss

    df["RSI"] = (
        100
        - (100 / (1 + rs))
    )

    ema12 = (
        df["Close"]
        .ewm(
            span=12,
            adjust=False,
        )
        .mean()
    )

    ema26 = (
        df["Close"]
        .ewm(
            span=26,
            adjust=False,
        )
        .mean()
    )

    df["MACD"] = (
        ema12 - ema26
    )

    df["MACD_Signal"] = (
        df["MACD"]
        .ewm(
            span=9,
            adjust=False,
        )
        .mean()
    )

    df["MACD_Histogram"] = (
        df["MACD"]
        - df["MACD_Signal"]
    )

    high_low = (
        df["High"]
        - df["Low"]
    )

    high_close = (
        df["High"]
        - df["Close"].shift(1)
    ).abs()

    low_close = (
        df["Low"]
        - df["Close"].shift(1)
    ).abs()

    true_range = np.maximum(
        high_low,
        np.maximum(
            high_close,
            low_close,
        ),
    )

    df["ATR"] = (
        true_range
        .rolling(window=14)
        .mean()
    )

    df["ATR_Percent"] = (
        df["ATR"]
        / df["Close"]
        * 100
    )

    df["Bollinger_Middle"] = (
        df["Close"]
        .rolling(window=20)
        .mean()
    )

    bollinger_std = (
        df["Close"]
        .rolling(window=20)
        .std()
    )

    df["Bollinger_Upper"] = (
        df["Bollinger_Middle"]
        + bollinger_std * 2
    )

    df["Bollinger_Lower"] = (
        df["Bollinger_Middle"]
        - bollinger_std * 2
    )

    bollinger_width = (
        df["Bollinger_Upper"]
        - df["Bollinger_Lower"]
    )

    df["Bollinger_Position"] = (
        (
            df["Close"]
            - df["Bollinger_Lower"]
        )
        / bollinger_width
    )

    df = df.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    return df