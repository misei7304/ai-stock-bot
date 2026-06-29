import yfinance as yf
import pandas as pd

from ml.ml_features import add_features, FEATURES


tickers = [
    "005930.KS",  # 삼성전자
    "000660.KS",  # SK하이닉스
    "035420.KS",  # NAVER
    "035720.KS",  # 카카오
    "051910.KS",  # LG화학
    "006400.KS",  # 삼성SDI
    "005380.KS",  # 현대차
    "000270.KS",  # 기아
    "068270.KS",  # 셀트리온
    "207940.KS",  # 삼성바이오로직스
]

all_data = []

for ticker in tickers:
    print(f"{ticker} 데이터 처리 중...")

    df = yf.download(ticker, period="5y", progress=False)

    if df.empty:
        print(f"{ticker}: 데이터 없음")
        continue

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = add_features(df)

    df["Future_Return_5D"] = df["Close"].shift(-5) / df["Close"] - 1
    df["Target"] = (df["Future_Return_5D"] >= 0.03).astype(int)
    df["Ticker"] = ticker

    df = df.dropna()

    dataset = df[["Ticker", "Close", "Future_Return_5D", "Target"] + FEATURES].copy()
    all_data.append(dataset)

if not all_data:
    print("생성된 데이터 없음")
else:
    final_df = pd.concat(all_data)

    final_df.to_csv("ml/training_dataset.csv")

    print("\n=== 통합 학습 데이터셋 생성 완료 ===")
    print(f"총 데이터 수: {len(final_df)}")
    print(f"종목 수: {final_df['Ticker'].nunique()}")
    print(f"저장 위치: ml/training_dataset.csv")