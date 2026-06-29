import pandas as pd

from ml.ml_features import FEATURES
from ml.ml_model import create_model


df = pd.read_csv("ml/training_dataset.csv")

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values(by="Date")

unique_dates = sorted(df["Date"].unique())

train_ratio = 0.8
split_index = int(len(unique_dates) * train_ratio)
split_date = unique_dates[split_index]

train_df = df[df["Date"] < split_date].copy()
test_df = df[df["Date"] >= split_date].copy()

X_train = train_df[FEATURES]
y_train = train_df["Target"]

X_test = test_df[FEATURES]

model = create_model()
model.fit(X_train, y_train)

test_df["Probability"] = model.predict_proba(X_test)[:, 1]

thresholds = [0.50, 0.60, 0.70, 0.80]

print("\n=== Walk-Forward 백테스트 ===")
print(f"학습 기간: {train_df['Date'].min().date()} ~ {train_df['Date'].max().date()}")
print(f"테스트 기간: {test_df['Date'].min().date()} ~ {test_df['Date'].max().date()}")

for threshold in thresholds:
    signal_df = test_df[test_df["Probability"] >= threshold].copy()

    if signal_df.empty:
        print(f"\n기준값 {threshold:.2f}: 신호 없음")
        continue

    trade_count = len(signal_df)
    win_rate = (signal_df["Future_Return_5D"] >= 0.03).mean()
    avg_return = signal_df["Future_Return_5D"].mean()
    median_return = signal_df["Future_Return_5D"].median()

    print(f"\n기준값: {threshold:.2f}")
    print(f"매수 신호 수: {trade_count}")
    print(f"5일 뒤 +3% 이상 성공률: {win_rate:.2%}")
    print(f"평균 5일 수익률: {avg_return:.2%}")
    print(f"중앙값 5일 수익률: {median_return:.2%}")

signal_df = test_df[test_df["Probability"] >= 0.70].copy()
signal_df.to_csv("ml/walk_forward_signals.csv", index=False)

print("\nCSV 저장 완료: ml/walk_forward_signals.csv")