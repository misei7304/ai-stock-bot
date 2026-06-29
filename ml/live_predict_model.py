import yfinance as yf
import pandas as pd

from ml.ml_features import add_features, FEATURES
from ml.ml_model import create_model


ticker = "005930.KS"
df = yf.download(ticker, period="5y")

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = add_features(df)


# 학습용 정답: 5일 뒤 +3% 이상 상승
df["Future_Return_5D"] = df["Close"].shift(-5) / df["Close"] - 1
df["Target"] = (df["Future_Return_5D"] >= 0.03).astype(int)


# 최신 예측용 데이터
latest_features_df = df.dropna(subset=FEATURES).copy()
latest = latest_features_df[FEATURES].tail(1)
latest_date = latest.index[0]
latest_close = latest_features_df.loc[latest_date, "Close"]

# 학습용 데이터
train_df = df.dropna(subset=FEATURES + ["Future_Return_5D", "Target"]).copy()

# 최신 데이터는 학습에서 제외
train_df = train_df[train_df.index < latest_date]

X = train_df[FEATURES]
y = train_df["Target"]


model = create_model()

model.fit(X, y)


up_probability = model.predict_proba(latest)[0][1]


print("\n=== 실시간 AI 예측 ===")
print(f"종목: 삼성전자 ({ticker})")
print(f"기준일: {latest_date.date()}")
print(f"종가: {latest_close:,.0f}원")
print(f"5일 내 +3% 이상 상승 확률: {up_probability:.2%}")

if up_probability >= 0.50:
    print("판단: 매수 후보")
else:
    print("판단: 매수 안 함")