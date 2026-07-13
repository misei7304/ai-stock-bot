import joblib
import pandas as pd

from ml.feature_subset_trade_backtest import (
    add_exit_date,
    calculate_trade_metrics,
    select_non_overlapping_trades,
)


DATASET_PATH = (
    "ml/training_dataset.csv"
)

MODEL_PATH = (
    "ml/trained_model.pkl"
)

SIGNAL_PATH = (
    "ml/trained_model_backtest_signals.csv"
)


def validate_model_data(
    model_data,
):
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
            "저장된 모델 설정에 필요한 "
            "항목이 없습니다: "
            + ", ".join(
                sorted(
                    missing_keys
                )
            )
        )


def validate_dataset(
    df,
    features,
):
    required_columns = {
        "Date",
        "Ticker",
        "Close",
        "Future_Return_5D",
        "Target",
        *features,
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "백테스트 데이터에 필요한 "
            "컬럼이 없습니다: "
            + ", ".join(
                sorted(
                    missing_columns
                )
            )
        )


def get_validation_dataframe(
    df,
):
    unique_dates = sorted(
        df["Date"].unique()
    )

    split_index = int(
        len(unique_dates)
        * 0.8
    )

    if (
        split_index <= 0
        or split_index
        >= len(unique_dates)
    ):
        raise ValueError(
            "날짜 기준 검증 구간을 "
            "생성할 수 없습니다."
        )

    split_date = unique_dates[
        split_index
    ]

    validation_df = df[
        df["Date"]
        >= split_date
    ].copy()

    if validation_df.empty:
        raise ValueError(
            "검증 데이터가 없습니다."
        )

    return validation_df


def run_trained_model_backtest():
    model_data = joblib.load(
        MODEL_PATH
    )

    validate_model_data(
        model_data
    )

    model = model_data[
        "model"
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

    df = pd.read_csv(
        DATASET_PATH
    )

    validate_dataset(
        df=df,
        features=features,
    )

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    df = (
        df.sort_values(
            by=[
                "Date",
                "Ticker",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    validation_df = (
        get_validation_dataframe(
            df
        )
    )

    X_validation = (
        validation_df[
            features
        ]
        .fillna(0)
    )

    validation_df[
        "Probability"
    ] = model.predict_proba(
        X_validation
    )[:, 1]

    validation_df[
        "Signal"
    ] = (
        validation_df[
            "Probability"
        ]
        >= threshold
    )

    raw_signal_df = validation_df[
        validation_df[
            "Signal"
        ]
        == True
    ].copy()

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "저장된 모델 검증 구간 백테스트"
    )

    print(
        "#"
        * 80
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
        f"검증 기간: "
        f"{validation_df['Date'].min().date()} "
        f"~ "
        f"{validation_df['Date'].max().date()}"
    )

    print(
        f"검증 데이터 수: "
        f"{len(validation_df):,}"
    )

    print(
        f"Threshold 통과 원시 신호 수: "
        f"{len(raw_signal_df):,}"
    )

    if raw_signal_df.empty:
        empty_df = pd.DataFrame(
            columns=[
                "Date",
                "Ticker",
                "Close",
                "Probability",
                "Future_Return_5D",
                "Target",
                "Signal",
                "Subset_Name",
                "Threshold",
                "Holding_Days",
            ]
        )

        empty_df.to_csv(
            SIGNAL_PATH,
            index=False,
        )

        print(
            "매수 신호가 없습니다."
        )

        print(
            "\nCSV 저장 완료: "
            f"{SIGNAL_PATH}"
        )

        return {
            "trade_count": 0,
            "candidate_trade_count": 0,
            "skipped_trade_count": 0,
            "total_return": 0.0,
            "final_money": 1_000_000,
            "max_drawdown": 0.0,
        }

    selected_signal_df = (
        select_non_overlapping_trades(
            raw_signal_df
        )
    )

    selected_signal_df = (
        add_exit_date(
            selected_signal_df
        )
    )

    metrics = (
        calculate_trade_metrics(
            selected_signal_df
        )
    )

    selected_signal_df[
        "Subset_Name"
    ] = subset_name

    selected_signal_df[
        "Threshold"
    ] = threshold

    selected_signal_df[
        "Holding_Days"
    ] = holding_days

    selected_signal_df[
        "Top_N_Signals"
    ] = top_n_signals

    selected_signal_df[
        "Max_Open_Positions"
    ] = max_open_positions

    selected_signal_df.to_csv(
        SIGNAL_PATH,
        index=False,
    )

    print(
        "\n=== 실제 거래 조건 적용 결과 ==="
    )

    print(
        f"선택 후보 거래 수: "
        f"{metrics['candidate_trade_count']:,}"
    )

    print(
        f"실제 체결 거래 수: "
        f"{metrics['trade_count']:,}"
    )

    print(
        f"보유 한도로 제외된 거래 수: "
        f"{metrics['skipped_trade_count']:,}"
    )

    if (
        metrics[
            "trade_count"
        ]
        > 0
    ):
        print(
            f"순수익 기준 +3% 성공률: "
            f"{metrics['success_rate_3pct']:.2%}"
        )

        print(
            f"순수익 발생률: "
            f"{metrics['profitable_rate']:.2%}"
        )

        print(
            f"평균 거래 순수익률: "
            f"{metrics['average_return']:.2%}"
        )

        print(
            f"중앙값 거래 순수익률: "
            f"{metrics['median_return']:.2%}"
        )

        print(
            f"누적 수익률: "
            f"{metrics['total_return']:.2%}"
        )

        print(
            f"최종 자산: "
            f"{metrics['final_money']:,.0f}원"
        )

        print(
            f"최대 낙폭: "
            f"{metrics['max_drawdown']:.2%}"
        )

        print(
            f"최고 거래: "
            f"{metrics['best_trade']:.2%}"
        )

        print(
            f"최악 거래: "
            f"{metrics['worst_trade']:.2%}"
        )

    print(
        "\n=== 최근 선택 신호 20개 ==="
    )

    display_columns = [
        "Date",
        "Ticker",
        "Close",
        "Probability",
        "Future_Return_5D",
        "Target",
        "Exit_Date",
    ]

    print(
        selected_signal_df[
            display_columns
        ]
        .tail(20)
        .to_string(
            index=False
        )
    )

    print(
        "\nCSV 저장 완료: "
        f"{SIGNAL_PATH}"
    )

    return metrics


if __name__ == "__main__":
    run_trained_model_backtest()