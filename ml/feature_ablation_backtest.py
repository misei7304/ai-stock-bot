import pandas as pd

from ml.ml_features import (
    ALL_FEATURES,
)
from ml.ml_model import create_model


DATASET_PATH = (
    "ml/training_dataset.csv"
)

RESULT_PATH = (
    "ml/feature_ablation_result.csv"
)

SIGNAL_THRESHOLD = 0.70


def validate_dataset(df):
    required_columns = {
        "Date",
        "Ticker",
        "Future_Return_5D",
        "Target",
        *ALL_FEATURES,
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "학습 데이터셋에 필요한 컬럼이 없습니다: "
            + ", ".join(
                sorted(missing_columns)
            )
        )


def calculate_signal_metrics(
    signal_df,
):
    if signal_df.empty:
        return {
            "total_trades": 0,
            "success_rate_3pct": None,
            "profitable_rate": None,
            "avg_return_5d": None,
            "median_return_5d": None,
            "return_std": None,
            "worst_return": None,
            "best_return": None,
        }

    returns = signal_df[
        "Future_Return_5D"
    ]

    return {
        "total_trades": len(
            signal_df
        ),
        "success_rate_3pct": (
            returns >= 0.03
        ).mean(),
        "profitable_rate": (
            returns > 0
        ).mean(),
        "avg_return_5d": (
            returns.mean()
        ),
        "median_return_5d": (
            returns.median()
        ),
        "return_std": (
            returns.std()
        ),
        "worst_return": (
            returns.min()
        ),
        "best_return": (
            returns.max()
        ),
    }


def run_single_ablation(
    df,
    unique_dates,
    train_window,
    test_window,
    step_size,
    removed_feature,
):
    if removed_feature is None:
        feature_list = list(
            ALL_FEATURES
        )

        experiment_name = (
            "baseline_all_features"
        )

    else:
        feature_list = [
            feature
            for feature in ALL_FEATURES
            if feature != removed_feature
        ]

        experiment_name = (
            f"remove_{removed_feature}"
        )

    print("\n" + "=" * 80)
    print(
        f"실험: {experiment_name}"
    )
    print(
        f"제거 Feature: "
        f"{removed_feature or '없음'}"
    )
    print(
        f"사용 Feature 수: "
        f"{len(feature_list)}"
    )
    print("=" * 80)

    all_signals = []

    fold = 1

    for start in range(
        0,
        (
            len(unique_dates)
            - train_window
            - test_window
        ),
        step_size,
    ):
        train_start = (
            unique_dates[start]
        )

        train_end = unique_dates[
            start
            + train_window
            - 1
        ]

        test_start = unique_dates[
            start
            + train_window
        ]

        test_end = unique_dates[
            start
            + train_window
            + test_window
            - 1
        ]

        train_df = df[
            (
                df["Date"]
                >= train_start
            )
            & (
                df["Date"]
                <= train_end
            )
        ].copy()

        test_df = df[
            (
                df["Date"]
                >= test_start
            )
            & (
                df["Date"]
                <= test_end
            )
        ].copy()

        X_train = (
            train_df[
                feature_list
            ]
            .fillna(0)
        )

        y_train = (
            train_df["Target"]
        )

        X_test = (
            test_df[
                feature_list
            ]
            .fillna(0)
        )

        model = create_model()

        model.fit(
            X_train,
            y_train,
        )

        probabilities = (
            model.predict_proba(
                X_test
            )[:, 1]
        )

        test_df[
            "Probability"
        ] = probabilities

        signal_df = test_df[
            test_df["Probability"]
            >= SIGNAL_THRESHOLD
        ].copy()

        if signal_df.empty:
            print(
                f"Fold {fold} | "
                "신호 없음"
            )

        else:
            fold_metrics = (
                calculate_signal_metrics(
                    signal_df
                )
            )

            print(
                f"Fold {fold} | "
                f"신호 "
                f"{fold_metrics['total_trades']}개 | "
                f"+3% 성공률 "
                f"{fold_metrics['success_rate_3pct']:.2%} | "
                f"평균수익 "
                f"{fold_metrics['avg_return_5d']:.2%}"
            )

            signal_result = signal_df[
                [
                    "Ticker",
                    "Date",
                    "Future_Return_5D",
                    "Probability",
                ]
            ].copy()

            signal_result[
                "fold"
            ] = fold

            all_signals.append(
                signal_result
            )

        fold += 1

    if not all_signals:
        metrics = (
            calculate_signal_metrics(
                pd.DataFrame()
            )
        )

    else:
        combined_signals = pd.concat(
            all_signals,
            ignore_index=True,
        )

        metrics = (
            calculate_signal_metrics(
                combined_signals
            )
        )

    result = {
        "experiment": (
            experiment_name
        ),
        "removed_feature": (
            removed_feature
            or "NONE"
        ),
        "feature_count": (
            len(feature_list)
        ),
        "threshold": (
            SIGNAL_THRESHOLD
        ),
        **metrics,
    }

    print("\n요약")
    print(
        f"총 신호 수: "
        f"{result['total_trades']}"
    )

    if result["total_trades"] > 0:
        print(
            "+3% 성공률: "
            f"{result['success_rate_3pct']:.2%}"
        )

        print(
            "수익 발생률: "
            f"{result['profitable_rate']:.2%}"
        )

        print(
            "평균 5일 수익률: "
            f"{result['avg_return_5d']:.2%}"
        )

        print(
            "중앙값 5일 수익률: "
            f"{result['median_return_5d']:.2%}"
        )

        print(
            "수익률 표준편차: "
            f"{result['return_std']:.2%}"
        )

        print(
            "최저 5일 수익률: "
            f"{result['worst_return']:.2%}"
        )

        print(
            "최고 5일 수익률: "
            f"{result['best_return']:.2%}"
        )

    return result


def add_baseline_differences(
    result_df,
):
    baseline_rows = result_df[
        result_df[
            "removed_feature"
        ] == "NONE"
    ]

    if baseline_rows.empty:
        raise ValueError(
            "기준 모델 결과가 없습니다."
        )

    baseline = (
        baseline_rows.iloc[0]
    )

    result_df[
        "avg_return_difference"
    ] = (
        result_df[
            "avg_return_5d"
        ]
        - baseline[
            "avg_return_5d"
        ]
    )

    result_df[
        "success_rate_difference"
    ] = (
        result_df[
            "success_rate_3pct"
        ]
        - baseline[
            "success_rate_3pct"
        ]
    )

    result_df[
        "profitable_rate_difference"
    ] = (
        result_df[
            "profitable_rate"
        ]
        - baseline[
            "profitable_rate"
        ]
    )

    result_df[
        "trade_count_difference"
    ] = (
        result_df[
            "total_trades"
        ]
        - baseline[
            "total_trades"
        ]
    )

    return result_df


def add_feature_effect_labels(
    result_df,
):
    def classify_effect(row):
        if (
            row["removed_feature"]
            == "NONE"
        ):
            return "baseline"

        avg_difference = row[
            "avg_return_difference"
        ]

        success_difference = row[
            "success_rate_difference"
        ]

        if pd.isna(
            avg_difference
        ):
            return "insufficient_signals"

        if (
            avg_difference > 0
            and success_difference > 0
        ):
            return (
                "removal_improved"
            )

        if (
            avg_difference < 0
            and success_difference < 0
        ):
            return (
                "feature_important"
            )

        if avg_difference < 0:
            return (
                "feature_helped_return"
            )

        if success_difference < 0:
            return (
                "feature_helped_success_rate"
            )

        return "mixed"

    result_df[
        "effect"
    ] = result_df.apply(
        classify_effect,
        axis=1,
    )

    return result_df


def run_feature_ablation_backtest():
    df = pd.read_csv(
        DATASET_PATH
    )

    validate_dataset(df)

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    df = df.sort_values(
        by="Date"
    )

    unique_dates = sorted(
        df["Date"].unique()
    )

    train_window = int(
        len(unique_dates)
        * 0.6
    )

    test_window = int(
        len(unique_dates)
        * 0.1
    )

    step_size = test_window

    if (
        train_window <= 0
        or test_window <= 0
    ):
        raise ValueError(
            "Walk-Forward 검증 기간을 "
            "생성할 데이터가 부족합니다."
        )

    print("\n" + "#" * 80)
    print("Feature Ablation Walk-Forward 검증")
    print("#" * 80)

    print(
        f"전체 Feature 수: "
        f"{len(ALL_FEATURES)}"
    )

    print(
        f"신호 기준값: "
        f"{SIGNAL_THRESHOLD:.2f}"
    )

    experiments = [
        None,
        *ALL_FEATURES,
    ]

    results = []

    for removed_feature in experiments:
        result = run_single_ablation(
            df=df,
            unique_dates=unique_dates,
            train_window=train_window,
            test_window=test_window,
            step_size=step_size,
            removed_feature=removed_feature,
        )

        results.append(
            result
        )

    result_df = pd.DataFrame(
        results
    )

    result_df = (
        add_baseline_differences(
            result_df
        )
    )

    result_df = (
        add_feature_effect_labels(
            result_df
        )
    )

    result_df = result_df.sort_values(
        by=[
            "avg_return_difference",
            "success_rate_difference",
            "total_trades",
        ],
        ascending=[
            False,
            False,
            False,
        ],
        na_position="last",
    ).reset_index(
        drop=True
    )

    result_df[
        "rank"
    ] = (
        result_df.index + 1
    )

    columns = [
        "rank",
        "experiment",
        "removed_feature",
        "effect",
        "feature_count",
        "threshold",
        "total_trades",
        "success_rate_3pct",
        "profitable_rate",
        "avg_return_5d",
        "median_return_5d",
        "return_std",
        "worst_return",
        "best_return",
        "avg_return_difference",
        "success_rate_difference",
        "profitable_rate_difference",
        "trade_count_difference",
    ]

    result_df = result_df[
        columns
    ]

    result_df.to_csv(
        RESULT_PATH,
        index=False,
    )

    print("\n" + "#" * 80)
    print("Feature Ablation 최종 비교")
    print("#" * 80)

    print(
        result_df.to_string(
            index=False
        )
    )

    print(
        "\n제거 후 성능이 개선된 Feature"
    )

    improved_df = result_df[
        result_df["effect"]
        == "removal_improved"
    ]

    if improved_df.empty:
        print(
            "제거 시 수익률과 성공률이 "
            "동시에 개선된 Feature가 없습니다."
        )

    else:
        for _, row in improved_df.iterrows():
            print(
                f"- {row['removed_feature']} 제거 | "
                f"평균수익 변화 "
                f"{row['avg_return_difference']:+.2%} | "
                f"성공률 변화 "
                f"{row['success_rate_difference']:+.2%}"
            )

    print(
        "\n제거 시 성능이 악화된 핵심 Feature"
    )

    important_df = result_df[
        result_df["effect"]
        == "feature_important"
    ].sort_values(
        by="avg_return_difference",
        ascending=True,
    )

    if important_df.empty:
        print(
            "수익률과 성공률이 동시에 "
            "악화된 Feature가 없습니다."
        )

    else:
        for _, row in important_df.iterrows():
            print(
                f"- {row['removed_feature']} 제거 | "
                f"평균수익 변화 "
                f"{row['avg_return_difference']:+.2%} | "
                f"성공률 변화 "
                f"{row['success_rate_difference']:+.2%}"
            )

    print(
        "\nCSV 저장 완료: "
        f"{RESULT_PATH}"
    )

    return result_df


if __name__ == "__main__":
    run_feature_ablation_backtest()