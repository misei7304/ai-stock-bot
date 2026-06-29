import yfinance as yf
import pandas as pd
import joblib

from ml.ml_features import add_features, FEATURES
from ml.ml_tickers import ML_TICKERS

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

MODEL_PATH = "ml/trained_model.pkl"
FINAL_CANDIDATES_PATH = "ml/final_candidates.csv"
SCAN_RESULTS_PATH = "ml/scan_results.csv"

AI_SIGNAL_THRESHOLD = 0.70

model = joblib.load(MODEL_PATH)

results = []

for ticker in ML_TICKERS:
    try:
        df = yf.download(ticker, period="5y", progress=False)

        if df.empty:
            print(f"{ticker}: 데이터 없음")
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = add_features(df)

        latest_features_df = df.dropna(subset=FEATURES).copy()

        if latest_features_df.empty:
            print(f"{ticker}: 최신 feature 데이터 없음")
            continue

        latest = latest_features_df[FEATURES].tail(1).fillna(0)
        latest_date = latest.index[0]
        latest_close = latest_features_df.loc[latest_date, "Close"]

        probability = model.predict_proba(latest)[0][1]

        results.append({
            "Ticker": ticker,
            "Date": latest_date.date(),
            "Close": latest_close,
            "Probability": probability,
            "Signal": probability >= AI_SIGNAL_THRESHOLD,
        })

        print(f"{ticker}: 상승확률 {probability:.2%}")

    except Exception as e:
        print(f"{ticker}: 에러 - {e}")


result_df = pd.DataFrame(results)

if result_df.empty:
    print("\n결과 없음")
else:
    result_df = result_df.sort_values(
        by="Probability",
        ascending=False
    )

    print("\n=== 저장된 통합 모델 스캔 결과 ===")
    print(result_df)

    passed_df = result_df[result_df["Signal"] == True].head(3)

    passed_df.to_csv(FINAL_CANDIDATES_PATH, index=False)
    result_df.to_csv(SCAN_RESULTS_PATH, index=False)

    print(f"\nAI 신호 기준값: {AI_SIGNAL_THRESHOLD:.2f}")
    print(f"최종 후보 저장 완료: {FINAL_CANDIDATES_PATH}")
    print(f"전체 결과 저장 완료: {SCAN_RESULTS_PATH}")