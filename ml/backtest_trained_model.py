import pandas as pd
import joblib

from ml.ml_features import FEATURES


df = pd.read_csv("ml/training_dataset.csv")
model = joblib.load("ml/trained_model.pkl")

X = df[FEATURES]

df["Probability"] = model.predict_proba(X)[:, 1]
df["Signal"] = df["Probability"] >= 0.70

signal_df = df[df["Signal"] == True].copy()

if signal_df.empty:
    print("매수 신호 없음")
else:
    trade_count = len(signal_df)
    win_rate = (signal_df["Future_Return_5D"] >= 0.03).mean()
    avg_return = signal_df["Future_Return_5D"].mean()
    total_return = (1 + signal_df["Future_Return_5D"]).prod() - 1

    print("\n=== 저장된 통합 모델 백테스트 ===")
    print(f"매수 신호 수: {trade_count}")
    print(f"5일 뒤 +3% 이상 성공률: {win_rate:.2%}")
    print(f"평균 5일 수익률: {avg_return:.2%}")
    print(f"누적 수익률: {total_return:.2%}")

    print("\n=== 최근 신호 20개 ===")
    print(
        signal_df[
            ["Ticker", "Close", "Probability", "Future_Return_5D", "Target"]
        ].tail(20)
    )

    signal_df.to_csv("ml/trained_model_backtest_signals.csv", index=False)
    print("\nCSV 저장 완료: ml/trained_model_backtest_signals.csv")