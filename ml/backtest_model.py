import joblib
import pandas as pd
import yfinance as yf

from ml.ml_features import (
    add_features,
)


MODEL_PATH = (
    "ml/trained_model.pkl"
)

SIGNAL_PATH = (
    "ml/signals.csv"
)

TICKER = "005930.KS"


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
            "저장된 모델 설정이 부족합니다: "
            + ", ".join(
                sorted(
                    missing_keys
                )
            )
        )

    if not model_data[
        "features"
    ]:
        raise ValueError(
            "저장된 Feature 목록이 "
            "비어 있습니다."
        )

    return model_data


def run_backtest():
    model_data = (
        load_trained_model_data()
    )

    model = model_data[
        "model"
    ]

    features = list(
        model_data[
            "features"
        ]
    )

    selected_threshold = float(
        model_data[
            "threshold"
        ]
    )

    subset_name = model_data[
        "subset_name"
    ]

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

    df = yf.download(
        TICKER,
        period="5y",
        progress=False,
        auto_adjust=False,
    )

    if df.empty:
        raise ValueError(
            f"{TICKER}: 주가 데이터가 없습니다."
        )

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

    df[
        "Future_Return_5D"
    ] = (
        df["Close"].shift(
            -holding_days
        )
        / df["Close"]
        - 1
    )

    df["Target"] = (
        df[
            "Future_Return_5D"
        ]
        >= 0.03
    ).astype(int)

    df = (
        df.dropna(
            subset=[
                *features,
                "Future_Return_5D",
                "Target",
            ]
        )
        .sort_index()
        .copy()
    )

    if df.empty:
        raise ValueError(
            "백테스트에 사용할 데이터가 "
            "없습니다."
        )

    split_index = int(
        len(df)
        * 0.8
    )

    if (
        split_index <= 0
        or split_index
        >= len(df)
    ):
        raise ValueError(
            "검증 구간을 생성할 수 없습니다."
        )

    test_df = (
        df.iloc[
            split_index:
        ]
        .copy()
    )

    X_test = (
        test_df[
            features
        ]
        .fillna(0)
    )

    test_df[
        "Up_Probability"
    ] = model.predict_proba(
        X_test
    )[:, 1]

    thresholds = sorted(
        {
            0.50,
            0.55,
            0.60,
            0.65,
            selected_threshold,
        }
    )

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "저장된 모델 기준값별 백테스트"
    )

    print(
        "#"
        * 80
    )

    print(
        f"종목: 삼성전자 "
        f"({TICKER})"
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
        f"저장된 Threshold: "
        f"{selected_threshold:.2f}"
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
        f"검증 기간: "
        f"{test_df.index.min().date()} "
        f"~ "
        f"{test_df.index.max().date()}"
    )

    print(
        f"검증 데이터 수: "
        f"{len(test_df):,}"
    )

    for threshold in thresholds:
        signal_mask = (
            test_df[
                "Up_Probability"
            ]
            >= threshold
        )

        signal_df = test_df[
            signal_mask
        ].copy()

        trade_count = int(
            len(signal_df)
        )

        if signal_df.empty:
            success_rate = None
            profitable_rate = None
            average_return = None
            total_return = 0.0

        else:
            returns = signal_df[
                "Future_Return_5D"
            ].astype(float)

            success_rate = float(
                (
                    returns
                    >= 0.03
                ).mean()
            )

            profitable_rate = float(
                (
                    returns
                    > 0
                ).mean()
            )

            average_return = float(
                returns.mean()
            )

            total_return = float(
                (
                    1
                    + returns
                ).prod()
                - 1
            )

        print(
            "\n"
            f"기준값: "
            f"{threshold:.2f}"
        )

        print(
            f"신호 수: "
            f"{trade_count:,}"
        )

        if trade_count == 0:
            print(
                "+3% 성공률: 신호 없음"
            )

            print(
                "수익 발생률: 신호 없음"
            )

            print(
                "평균 5일 수익률: 신호 없음"
            )

        else:
            print(
                f"+3% 성공률: "
                f"{success_rate:.2%}"
            )

            print(
                f"수익 발생률: "
                f"{profitable_rate:.2%}"
            )

            print(
                f"평균 5일 수익률: "
                f"{average_return:.2%}"
            )

        print(
            f"단순 신호 복리 수익률: "
            f"{total_return:.2%}"
        )

    selected_signal_df = test_df[
        test_df[
            "Up_Probability"
        ]
        >= selected_threshold
    ].copy()

    selected_signal_df[
        "Signal"
    ] = True

    selected_signal_df[
        "Subset_Name"
    ] = subset_name

    selected_signal_df[
        "Threshold"
    ] = selected_threshold

    selected_signal_df[
        "Holding_Days"
    ] = holding_days

    selected_signal_df[
        "Top_N_Signals"
    ] = top_n_signals

    selected_signal_df[
        "Max_Open_Positions"
    ] = max_open_positions

    print(
        f"\n=== "
        f"{selected_threshold:.2f} "
        "기준 매수 신호 목록 ==="
    )

    display_columns = [
        "Close",
        "Up_Probability",
        "Future_Return_5D",
        "Target",
    ]

    if selected_signal_df.empty:
        print(
            "선택된 Threshold를 통과한 "
            "신호가 없습니다."
        )

    else:
        print(
            selected_signal_df[
                display_columns
            ]
            .to_string()
        )

    selected_signal_df.to_csv(
        SIGNAL_PATH,
        index=True,
        index_label="Date",
    )

    print(
        "\nCSV 저장 완료: "
        f"{SIGNAL_PATH}"
    )

    return selected_signal_df


if __name__ == "__main__":
    run_backtest()