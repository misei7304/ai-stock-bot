import pandas as pd
import yfinance as yf

from ml.ml_features import (
    ALL_FEATURES,
    add_features,
)
from ml.ml_tickers import ML_TICKERS


DATASET_PATH = (
    "ml/training_dataset.csv"
)


def build_training_dataset():
    all_data = []

    for ticker in ML_TICKERS:
        print(
            f"{ticker} 데이터 처리 중..."
        )

        try:
            df = yf.download(
                ticker,
                period="5y",
                progress=False,
            )

            if df.empty:
                print(
                    f"{ticker}: 데이터 없음"
                )
                continue

            if isinstance(
                df.columns,
                pd.MultiIndex,
            ):
                df.columns = (
                    df.columns
                    .get_level_values(0)
                )

            df = add_features(df)

            df["Future_Return_5D"] = (
                df["Close"].shift(-5)
                / df["Close"]
                - 1
            )

            df["Target"] = (
                df["Future_Return_5D"]
                >= 0.03
            ).astype(int)

            df["Ticker"] = ticker

            required_columns = [
                "Close",
                "Future_Return_5D",
                "Target",
                *ALL_FEATURES,
            ]

            df = df.dropna(
                subset=required_columns
            )

            dataset = df[
                [
                    "Ticker",
                    "Close",
                    "Future_Return_5D",
                    "Target",
                    *ALL_FEATURES,
                ]
            ].copy()

            all_data.append(dataset)

            print(
                f"{ticker}: "
                f"{len(dataset)}개 저장 대상"
            )

        except Exception as error:
            print(
                f"{ticker}: "
                f"처리 실패 - {error}"
            )

    if not all_data:
        print("생성된 데이터 없음")
        return None

    final_df = pd.concat(
        all_data
    )

    final_df.index.name = "Date"

    final_df.to_csv(
        DATASET_PATH
    )

    print(
        "\n=== 통합 학습 데이터셋 "
        "생성 완료 ==="
    )

    print(
        f"총 데이터 수: "
        f"{len(final_df):,}"
    )

    print(
        f"종목 수: "
        f"{final_df['Ticker'].nunique()}"
    )

    print(
        f"Feature 수: "
        f"{len(ALL_FEATURES)}"
    )

    print(
        f"저장 위치: "
        f"{DATASET_PATH}"
    )

    return final_df


if __name__ == "__main__":
    build_training_dataset()