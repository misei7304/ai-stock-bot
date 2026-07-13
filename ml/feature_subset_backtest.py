import pandas as pd

from ml.ml_features import (
    ALL_FEATURES,
)
from ml.ml_model import create_model


DATASET_PATH = (
    "ml/training_dataset.csv"
)

RESULT_PATH = (
    "ml/feature_subset_result.csv"
)


FEATURE_SUBSETS = {
    "all_16_features": list(
        ALL_FEATURES
    ),

    "remove_4_harmful_features": [
        feature
        for feature in ALL_FEATURES
        if feature not in {
            "ATR_Percent",
            "Momentum_5",
            "Distance_From_20D_High",
            "High_Low_Range",
        }
    ],

    "core_10_features": [
        "MA120_Ratio",
        "MACD",
        "ATR",
        "RSI",
        "MA60",
        "OBV_Imbalance_20",
        "Momentum_10",
        "Turnover_Ratio_20",
        "MACD_Signal",
        "Volume_Ratio_20",
    ],

    "core_plus_ma60_ratio": [
        "MA120_Ratio",
        "MACD",
        "ATR",
        "RSI",
        "MA60",
        "MA60_Ratio",
        "OBV_Imbalance_20",
        "Momentum_10",
        "Turnover_Ratio_20",
        "MACD_Signal",
        "Volume_Ratio_20",
    ],

    "importance_top_10": [
        "ATR_Percent",
        "High_Low_Range",
        "Volatility_20",
        "MA120_Ratio",
        "MA60_Ratio",
        "Momentum_5",
        "ATR",
        "MACD",
        "Momentum_10",
        "Distance_From_20D_High",
    ],
}


THRESHOLDS = [
    0.70,
    0.75,
    0.80,
]


def validate_dataset(
    df,
):
    required_columns = {
        "Date",
        "Ticker",
        "Future_Return_5D",
        "Target",
    }

    for feature_list in (
        FEATURE_SUBSETS.values()
    ):
        required_columns.update(
            feature_list
        )

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "학습 데이터셋에 필요한 "
            "컬럼이 없습니다: "
            + ", ".join(
                sorted(
                    missing_columns
                )
            )
        )


def validate_feature_subsets():
    known_features = set(
        ALL_FEATURES
    )

    for (
        subset_name,
        feature_list,
    ) in FEATURE_SUBSETS.items():
        if not feature_list:
            raise ValueError(
                f"{subset_name}: "
                "Feature 목록이 비어 있습니다."
            )

        duplicated_features = [
            feature
            for feature in feature_list
            if feature_list.count(
                feature
            ) > 1
        ]

        if duplicated_features:
            raise ValueError(
                f"{subset_name}: "
                "중복 Feature가 있습니다: "
                + ", ".join(
                    sorted(
                        set(
                            duplicated_features
                        )
                    )
                )
            )

        unknown_features = (
            set(feature_list)
            - known_features
        )

        if unknown_features:
            raise ValueError(
                f"{subset_name}: "
                "ALL_FEATURES에 없는 "
                "Feature가 있습니다: "
                + ", ".join(
                    sorted(
                        unknown_features
                    )
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
        "total_trades": int(
            len(signal_df)
        ),
        "success_rate_3pct": float(
            (
                returns >= 0.03
            ).mean()
        ),
        "profitable_rate": float(
            (
                returns > 0
            ).mean()
        ),
        "avg_return_5d": float(
            returns.mean()
        ),
        "median_return_5d": float(
            returns.median()
        ),
        "return_std": float(
            returns.std()
        ),
        "worst_return": float(
            returns.min()
        ),
        "best_return": float(
            returns.max()
        ),
    }


def run_single_subset_backtest(
    df,
    unique_dates,
    train_window,
    test_window,
    step_size,
    subset_name,
    feature_list,
    threshold,
):
    print("\n" + "=" * 80)
    print(
        f"Feature Subset: "
        f"{subset_name}"
    )
    print(
        f"Feature 수: "
        f"{len(feature_list)}"
    )
    print(
        f"신호 기준값: "
        f"{threshold:.2f}"
    )
    print("=" * 80)

    print(
        "사용 Feature: "
        + ", ".join(
            feature_list
        )
    )

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

        if X_train.empty:
            print(
                f"Fold {fold} | "
                "학습 데이터 없음"
            )

            fold += 1
            continue

        if X_test.empty:
            print(
                f"Fold {fold} | "
                "검증 데이터 없음"
            )

            fold += 1
            continue

        if (
            y_train.nunique()
            < 2
        ):
            print(
                f"Fold {fold} | "
                "학습 Target 클래스 부족"
            )

            fold += 1
            continue

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
            >= threshold
        ].copy()

        if signal_df.empty:
            print(
                f"Fold {fold} | "
                "신호 없음"
            )

            fold += 1
            continue

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
        combined_signals = (
            pd.DataFrame()
        )

    else:
        combined_signals = pd.concat(
            all_signals,
            ignore_index=True,
        )

    metrics = calculate_signal_metrics(
        combined_signals
    )

    result = {
        "subset_name": subset_name,
        "feature_count": len(
            feature_list
        ),
        "features": "|".join(
            feature_list
        ),
        "threshold": threshold,
        **metrics,
    }

    print("\n요약")
    print(
        f"총 신호 수: "
        f"{result['total_trades']}"
    )

    if (
        result["total_trades"]
        > 0
    ):
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
    baseline_df = result_df[
        result_df[
            "subset_name"
        ] == "all_16_features"
    ][
        [
            "threshold",
            "total_trades",
            "success_rate_3pct",
            "profitable_rate",
            "avg_return_5d",
        ]
    ].copy()

    if baseline_df.empty:
        raise ValueError(
            "all_16_features "
            "기준 결과가 없습니다."
        )

    baseline_df = baseline_df.rename(
        columns={
            "total_trades": (
                "baseline_total_trades"
            ),
            "success_rate_3pct": (
                "baseline_success_rate_3pct"
            ),
            "profitable_rate": (
                "baseline_profitable_rate"
            ),
            "avg_return_5d": (
                "baseline_avg_return_5d"
            ),
        }
    )

    result_df = result_df.merge(
        baseline_df,
        on="threshold",
        how="left",
    )

    result_df[
        "trade_count_difference"
    ] = (
        result_df[
            "total_trades"
        ]
        - result_df[
            "baseline_total_trades"
        ]
    )

    result_df[
        "success_rate_difference"
    ] = (
        result_df[
            "success_rate_3pct"
        ]
        - result_df[
            "baseline_success_rate_3pct"
        ]
    )

    result_df[
        "profitable_rate_difference"
    ] = (
        result_df[
            "profitable_rate"
        ]
        - result_df[
            "baseline_profitable_rate"
        ]
    )

    result_df[
        "avg_return_difference"
    ] = (
        result_df[
            "avg_return_5d"
        ]
        - result_df[
            "baseline_avg_return_5d"
        ]
    )

    return result_df


def calculate_subset_score(
    result_df,
):
    minimum_trades = 20

    result_df[
        "sample_penalty"
    ] = (
        result_df[
            "total_trades"
        ]
        .clip(
            upper=minimum_trades
        )
        / minimum_trades
    )

    result_df[
        "subset_score"
    ] = (
        result_df[
            "avg_return_5d"
        ]
        * 0.45
        + result_df[
            "success_rate_3pct"
        ]
        * 0.25
        + result_df[
            "profitable_rate"
        ]
        * 0.20
        + result_df[
            "sample_penalty"
        ]
        * 0.10
    )

    result_df.loc[
        result_df[
            "total_trades"
        ] == 0,
        "subset_score",
    ] = None

    return result_df


def run_feature_subset_backtest():
    validate_feature_subsets()

    df = pd.read_csv(
        DATASET_PATH
    )

    validate_dataset(
        df
    )

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
        or step_size <= 0
    ):
        raise ValueError(
            "Walk-Forward 검증 기간을 "
            "생성할 데이터가 부족합니다."
        )

    print("\n" + "#" * 80)
    print(
        "Feature Subset "
        "Walk-Forward 검증"
    )
    print("#" * 80)

    print(
        f"비교 Feature Subset 수: "
        f"{len(FEATURE_SUBSETS)}"
    )

    print(
        "검증 기준값: "
        + ", ".join(
            f"{threshold:.2f}"
            for threshold in THRESHOLDS
        )
    )

    results = []

    for (
        subset_name,
        feature_list,
    ) in FEATURE_SUBSETS.items():
        for threshold in THRESHOLDS:
            result = (
                run_single_subset_backtest(
                    df=df,
                    unique_dates=unique_dates,
                    train_window=train_window,
                    test_window=test_window,
                    step_size=step_size,
                    subset_name=subset_name,
                    feature_list=feature_list,
                    threshold=threshold,
                )
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
        calculate_subset_score(
            result_df
        )
    )

    result_df = result_df.sort_values(
        by=[
            "threshold",
            "subset_score",
            "avg_return_5d",
            "success_rate_3pct",
            "total_trades",
        ],
        ascending=[
            True,
            False,
            False,
            False,
            False,
        ],
        na_position="last",
    ).reset_index(
        drop=True
    )

    result_df[
        "rank_within_threshold"
    ] = (
        result_df.groupby(
            "threshold"
        ).cumcount()
        + 1
    )

    output_columns = [
        "rank_within_threshold",
        "subset_name",
        "threshold",
        "feature_count",
        "total_trades",
        "success_rate_3pct",
        "profitable_rate",
        "avg_return_5d",
        "median_return_5d",
        "return_std",
        "worst_return",
        "best_return",
        "trade_count_difference",
        "success_rate_difference",
        "profitable_rate_difference",
        "avg_return_difference",
        "sample_penalty",
        "subset_score",
        "features",
    ]

    result_df = result_df[
        output_columns
    ]

    result_df.to_csv(
        RESULT_PATH,
        index=False,
    )

    print("\n" + "#" * 80)
    print("Feature Subset 최종 비교")
    print("#" * 80)

    display_columns = [
        "rank_within_threshold",
        "subset_name",
        "threshold",
        "feature_count",
        "total_trades",
        "success_rate_3pct",
        "profitable_rate",
        "avg_return_5d",
        "median_return_5d",
        "worst_return",
        "avg_return_difference",
        "success_rate_difference",
        "subset_score",
    ]

    print(
        result_df[
            display_columns
        ].to_string(
            index=False
        )
    )

    print(
        "\n임계값별 1위"
    )

    best_by_threshold = result_df[
        result_df[
            "rank_within_threshold"
        ] == 1
    ]

    for _, row in (
        best_by_threshold.iterrows()
    ):
        print(
            f"- 기준값 "
            f"{row['threshold']:.2f} | "
            f"{row['subset_name']} | "
            f"Feature "
            f"{int(row['feature_count'])}개 | "
            f"신호 "
            f"{int(row['total_trades'])}개 | "
            f"+3% 성공률 "
            f"{row['success_rate_3pct']:.2%} | "
            f"평균수익 "
            f"{row['avg_return_5d']:.2%}"
        )

    print(
        "\nCSV 저장 완료: "
        f"{RESULT_PATH}"
    )

    return result_df


if __name__ == "__main__":
    run_feature_subset_backtest()