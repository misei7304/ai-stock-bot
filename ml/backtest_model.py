import yfinance as yf
import pandas as pd

from sklearn.model_selection import train_test_split
from ml.ml_features import add_features, FEATURES
from ml.ml_model import create_model


ticker = "005930.KS"
df = yf.download(ticker, period="5y")

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = add_features(df)


# 5일 뒤 수익률
df["Future_Return_5D"] = df["Close"].shift(-5) / df["Close"] - 1

# 5일 뒤 수익률이 +3% 이상이면 1, 아니면 0
df["Target"] = (df["Future_Return_5D"] >= 0.03).astype(int)

df = df.dropna()

X = df[FEATURES]
y = df["Target"]


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

test_df = df.loc[X_test.index].copy()


model = create_model()

model.fit(X_train, y_train)


# 상승 확률
test_df["Up_Probability"] = model.predict_proba(X_test)[:, 1]

thresholds = [0.50, 0.55, 0.60, 0.65, 0.70]

print("\n=== 기준값별 백테스트 ===")

for threshold in thresholds:
    test_df["Signal"] = test_df["Up_Probability"] >= threshold

    test_df["Strategy_Return"] = 0.0
    test_df.loc[test_df["Signal"], "Strategy_Return"] = test_df.loc[
        test_df["Signal"], "Future_Return_5D"
    ]

    strategy_total_return = (1 + test_df["Strategy_Return"]).prod() - 1
    trade_count = test_df["Signal"].sum()

    if trade_count > 0:
        win_rate = (test_df.loc[test_df["Signal"], "Strategy_Return"] > 0).mean()
        avg_trade_return = test_df.loc[test_df["Signal"], "Strategy_Return"].mean()
    else:
        win_rate = 0
        avg_trade_return = 0

    print(f"\n기준값: {threshold:.2f}")
    print(f"매수 횟수: {trade_count}")
    print(f"AI 전략 누적 수익률: {strategy_total_return:.2%}")
    print(f"승률: {win_rate:.2%}")
    print(f"평균 거래 수익률: {avg_trade_return:.2%}")

print("\n=== 0.50 기준 매수 신호 목록 ===")
test_df["Signal"] = test_df["Up_Probability"] >= 0.50
print(
    test_df[test_df["Signal"]][
        ["Close", "Up_Probability", "Future_Return_5D"]
    ]
)

signal_df = test_df[test_df["Up_Probability"] >= 0.50][
    ["Close", "Up_Probability", "Future_Return_5D"]
]

signal_df.to_csv("ml/signals.csv")

print("\nCSV 저장 완료: signals.csv")