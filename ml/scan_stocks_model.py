import joblib
import pandas as pd
import yfinance as yf

from ml.ml_features import (
    add_features,
)
from ml.ml_tickers import (
    ML_TICKERS,
)


MODEL_PATH = (
    "ml/trained_model.pkl"
)

FINAL_CANDIDATES_PATH = (
    "ml/final_candidates.csv"
)

SCAN_RESULTS_PATH = (
    "ml/scan_results.csv"
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
            "저장된 모델 형식이 올바르지 않습니다. "
            "ml/train_model.py를 다시 실행하세요."
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
            "저장된 모델 설정에 필요한 항목이 없습니다: "
            + ", ".join(
                sorted(
                    missing_keys
                )
            )
        )

    features = model_data[
        "features"
    ]

    if not features:
        raise ValueError(
            "저장된 모델의 Feature 목록이 비어 있습니다."
        )

    return model_data


def validate_feature_columns(
    df,
    ticker,
    features,
):
    missing_features = [
        feature
        for feature in features
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"{ticker}: 생성되지 않은 Feature가 있습니다: "
            + ", ".join(
                missing_features
            )
        )


def create_empty_result_dataframe():
    return pd.DataFrame(
        columns=[
            "Ticker",
            "Date",
            "Close",
            "Probability",
            "Signal",
            "Subset_Name",
            "Threshold",
        ]
    )


def scan_stocks_model():
    model_data = (
        load_trained_model_data()
    )

    model = model_data[
        "model"
    ]

    subset_name = model_data[
        "subset_name"
    ]

    features = list(
        model_data[
            "features"
        ]
    )

    threshold = float(
        model_data[
            "threshold"
        ]
    )

    holding_days = int(
        model_data[
            "holding_days"
        ]
    )

    top_n_signals = int(
        model_data[
            "top_n_signals"
        ]
    )

    max_open_positions = int(
        model_data[
            "max_open_positions"
        ]
    )

    print(
        "\n선택된 모델 설정"
    )

    print(
        f"Feature Subset: "
        f"{subset_name}"
    )

    print(
        f"Feature 수: "
        f"{len(features)}"
    )

    print(
        "Features: "
        + ", ".join(
            features
        )
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

    results = []

    for ticker in ML_TICKERS:
        try:
            df = yf.download(
                ticker,
                period="5y",
                progress=False,
                auto_adjust=False,
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

            df = add_features(
                df
            )

            validate_feature_columns(
                df=df,
                ticker=ticker,
                features=features,
            )

            latest_features_df = (
                df.dropna(
                    subset=features
                )
                .copy()
            )

            if latest_features_df.empty:
                print(
                    f"{ticker}: "
                    "최신 Feature 데이터 없음"
                )
                continue

            latest_date = (
                latest_features_df
                .index[-1]
            )

            latest = (
                latest_features_df.loc[
                    [
                        latest_date
                    ],
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

            probability = float(
                model.predict_proba(
                    latest
                )[0][1]
            )

            signal = (
                probability
                >= threshold
            )

            results.append({
                "Ticker": ticker,
                "Date": (
                    latest_date.date()
                ),
                "Close": latest_close,
                "Probability": (
                    probability
                ),
                "Signal": signal,
                "Subset_Name": (
                    subset_name
                ),
                "Threshold": (
                    threshold
                ),
            })

            print(
                f"{ticker}: "
                f"상승확률 "
                f"{probability:.2%} | "
                f"Signal "
                f"{signal}"
            )

        except Exception as error:
            print(
                f"{ticker}: "
                f"에러 - {error}"
            )

    result_df = pd.DataFrame(
        results
    )

    if result_df.empty:
        empty_result_df = (
            create_empty_result_dataframe()
        )

        empty_result_df.to_csv(
            FINAL_CANDIDATES_PATH,
            index=False,
        )

        empty_result_df.to_csv(
            SCAN_RESULTS_PATH,
            index=False,
        )

        print(
            "\nAI 스캔 결과가 없습니다."
        )

        return []

    result_df = (
        result_df
        .sort_values(
            by=[
                "Probability",
                "Ticker",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    passed_df = (
        result_df[
            result_df[
                "Signal"
            ]
            == True
        ]
        .head(
            top_n_signals
        )
        .copy()
    )

    passed_df.to_csv(
        FINAL_CANDIDATES_PATH,
        index=False,
    )

    result_df.to_csv(
        SCAN_RESULTS_PATH,
        index=False,
    )

    print(
        "\nAI 신호 기준값: "
        f"{threshold:.2f}"
    )

    print(
        "최종 AI 후보 수: "
        f"{len(passed_df)}개"
    )

    print(
        "최종 후보 제한 수: "
        f"{top_n_signals}개"
    )

    print(
        "최대 보유 가능 종목 수: "
        f"{max_open_positions}개"
    )

    print(
        "최종 후보 저장 완료: "
        f"{FINAL_CANDIDATES_PATH}"
    )

    print(
        "전체 결과 저장 완료: "
        f"{SCAN_RESULTS_PATH}"
    )

    return passed_df.to_dict(
        orient="records"
    )


if __name__ == "__main__":
    pd.set_option(
        "display.max_columns",
        None,
    )

    pd.set_option(
        "display.width",
        200,
    )

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "AI 종목 스캔"
    )

    print(
        "#"
        * 80
    )

    scan_results = (
        scan_stocks_model()
    )

    if not scan_results:
        print(
            "AI 기준 통과 종목이 없습니다."
        )

    else:
        print(
            "\n최종 AI 후보"
        )

        for result in scan_results:
            print(
                f"{result['Ticker']} | "
                f"확률 "
                f"{result['Probability']:.2%} | "
                f"기준일 "
                f"{result['Date']} | "
                f"기준가 "
                f"{result['Close']:,.0f}원 | "
                f"Subset "
                f"{result['Subset_Name']}"
            )