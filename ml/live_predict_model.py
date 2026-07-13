import joblib
import pandas as pd
import yfinance as yf

from ml.ml_features import (
    add_features,
)


MODEL_PATH = (
    "ml/trained_model.pkl"
)


def load_trained_model_data():
    model_data = joblib.load(
        MODEL_PATH
    )

    if not isinstance(
        model_data,
        dict,
    ):
        raise ValueError(
            "저장된 모델 형식이 올바르지 않습니다."
        )

    required_keys = {
        "model",
        "subset_name",
        "features",
        "threshold",
        "holding_days",
        "top_n_signals",
        "max_open_positions",
    }

    missing_keys = (
        required_keys
        - set(
            model_data.keys()
        )
    )

    if missing_keys:
        raise ValueError(
            "저장된 모델 설정이 부족합니다: "
            + ", ".join(
                sorted(
                    missing_keys
                )
            )
        )

    return model_data


ticker = "005930.KS"

df = yf.download(
    ticker,
    period="5y",
    progress=False,
    auto_adjust=False,
)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = add_features(
    df
)

model_data = (
    load_trained_model_data()
)

model = model_data["model"]
features = list(model_data["features"])
threshold = float(model_data["threshold"])
subset_name = model_data["subset_name"]
holding_days = int(model_data["holding_days"])
top_n_signals = int(model_data["top_n_signals"])
max_open_positions = int(model_data["max_open_positions"])

missing_features = [
    feature
    for feature in features
    if feature not in df.columns
]

if missing_features:
    raise ValueError(
        "생성되지 않은 Feature가 있습니다: "
        + ", ".join(
            missing_features
        )
    )

latest_features_df = (
    df.dropna(
        subset=features
    )
    .copy()
)

if latest_features_df.empty:
    raise ValueError(
        "최신 예측에 사용할 "
        "Feature 데이터가 없습니다."
    )

latest_date = (
    latest_features_df.index[-1]
)

latest = (
    latest_features_df.loc[
        [latest_date],
        features,
    ]
    .fillna(0)
)

latest_close = float(
    latest_features_df.loc[
        latest_date,
        "Close",
    ]
)


up_probability = float(
    model.predict_proba(
        latest
    )[0][1]
)

print("\n" + "#" * 80)
print("실시간 AI 예측")
print("#" * 80)

print(
    f"Feature Subset: "
    f"{subset_name}"
)

print(
    f"Feature 수: "
    f"{len(features)}"
)

print(
    f"Threshold: "
    f"{threshold:.2f}"
)

print(
    f"Holding Days: "
    f"{holding_days}"
)

print(
    f"Top N Signals: "
    f"{top_n_signals}"
)

print(
    f"Max Open Positions: "
    f"{max_open_positions}"
)

print(
    f"종목: 삼성전자 "
    f"({ticker})"
)

print(
    f"기준일: "
    f"{latest_date.date()}"
)

print(
    f"종가: "
    f"{latest_close:,.0f}원"
)

print(
    "5일 내 +3% 이상 상승 확률: "
    f"{up_probability:.2%}"
)

if (
    up_probability
    >= threshold
):
    print("판단: 매수 후보")
else:
    print("판단: 매수 안 함")