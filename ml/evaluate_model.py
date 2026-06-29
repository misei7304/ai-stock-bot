import yfinance as yf
import pandas as pd

from sklearn.model_selection import train_test_split

from ml.ml_features import add_features, FEATURES
from ml.ml_model import create_model


def evaluate_ticker(ticker, threshold=0.50):
    df = yf.download(ticker, period="5y", progress=False)

    if df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = add_features(df)

    df["Future_Return_5D"] = df["Close"].shift(-5) / df["Close"] - 1
    df["Target"] = (df["Future_Return_5D"] >= 0.03).astype(int)

    df = df.dropna()

    if len(df) < 300:
        return None

    X = df[FEATURES]
    y = df["Target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    test_df = df.loc[X_test.index].copy()

    model = create_model()
    model.fit(X_train, y_train)

    test_df["Up_Probability"] = model.predict_proba(X_test)[:, 1]
    test_df["Signal"] = test_df["Up_Probability"] >= threshold

    test_df["Strategy_Return"] = 0.0
    test_df.loc[test_df["Signal"], "Strategy_Return"] = test_df.loc[
        test_df["Signal"], "Future_Return_5D"
    ]

    trade_count = int(test_df["Signal"].sum())

    if trade_count > 0:
        win_rate = (test_df.loc[test_df["Signal"], "Strategy_Return"] > 0).mean()
        avg_trade_return = test_df.loc[test_df["Signal"], "Strategy_Return"].mean()
        total_return = (1 + test_df["Strategy_Return"]).prod() - 1
    else:
        win_rate = 0
        avg_trade_return = 0
        total_return = 0

    # 실시간 예측용: 최신 날짜는 학습에서 제외
    latest_features_df = df.dropna(subset=FEATURES).copy()
    latest = latest_features_df[FEATURES].tail(1)
    latest_date = latest.index[0]
    latest_close = latest_features_df.loc[latest_date, "Close"]

    train_df = df[df.index < latest_date].copy()

    X_live = train_df[FEATURES]
    y_live = train_df["Target"]

    live_model = create_model()
    live_model.fit(X_live, y_live)

    current_probability = live_model.predict_proba(latest)[0][1]

    trade_score = min(trade_count / 100, 1.0)

    score = (
        current_probability * 0.4
        + win_rate * 0.4
        + trade_score * 0.2
    )

    return {
        "Ticker": ticker,
        "Date": latest_date.date(),
        "Close": latest_close,
        "Current_Probability": current_probability,
        "Signal": current_probability >= threshold,
        "Trade_Count": trade_count,
        "Win_Rate": win_rate,
        "Avg_Trade_Return": avg_trade_return,
        "Total_Return": total_return,
        "Score": score,
    }