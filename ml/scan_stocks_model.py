import yfinance as yf
import pandas as pd
import joblib

from ml.ml_features import add_features, FEATURES
from ml.ml_tickers import ML_TICKERS

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)


model = joblib.load("ml/trained_model.pkl")

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

        latest = latest_features_df[FEATURES].tail(1)
        latest_date = latest.index[0]
        latest_close = latest_features_df.loc[latest_date, "Close"]

        probability = model.predict_proba(latest)[0][1]

        results.append({
            "Ticker": ticker,
            "Date": latest_date.date(),
            "Close": latest_close,
            "Probability": probability,
            "Signal": probability >= 0.60,
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

    passed_df.to_csv("ml/final_candidates.csv", index=False)
    result_df.to_csv("ml/scan_results.csv", index=False)

    print("\n최종 후보 저장 완료: ml/final_candidates.csv")
    print("전체 결과 저장 완료: ml/scan_results.csv")