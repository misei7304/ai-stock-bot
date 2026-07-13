import joblib
import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
)
from sklearn.metrics import (
    accuracy_score,
)


MODEL_PATH = (
    "ml/trained_model.pkl"
)

DATASET_PATH = (
    "ml/training_dataset.csv"
)

RESULT_PATH = (
    "ml/hyperparameter_tuning_result.csv"
)


PARAM_SETS = [
    {
        "n_estimators": 200,
        "max_depth": 5,
        "min_samples_leaf": 5,
    },
    {
        "n_estimators": 300,
        "max_depth": 5,
        "min_samples_leaf": 5,
    },
    {
        "n_estimators": 300,
        "max_depth": 7,
        "min_samples_leaf": 5,
    },
    {
        "n_estimators": 300,
        "max_depth": 10,
        "min_samples_leaf": 5,
    },
    {
        "n_estimators": 500,
        "max_depth": 7,
        "min_samples_leaf": 5,
    },
    {
        "n_estimators": 500,
        "max_depth": 10,
        "min_samples_leaf": 5,
    },
    {
        "n_estimators": 500,
        "max_depth": 10,
        "min_samples_leaf": 10,
    },
]


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


def validate_dataset(
    df,
    features,
):
    required_columns = {
        "Date",
        "Ticker",
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
            "Hyperparameter Tuning 데이터에 "
            "필요한 컬럼이 없습니다: "
            + ", ".join(
                sorted(
                    missing_columns
                )
            )
        )


def create_tuning_model(
    params,
):
    return RandomForestClassifier(
        n_estimators=(
            params[
                "n_estimators"
            ]
        ),
        max_depth=(
            params[
                "max_depth"
            ]
        ),
        min_samples_leaf=(
            params[
                "min_samples_leaf"
            ]
        ),
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )


def run_tuning():
    model_data = (
        load_trained_model_data()
    )

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
            "Walk-Forward 검증 구간을 "
            "생성할 수 없습니다."
        )

    results = []

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "Hyperparameter Tuning "
        "Walk-Forward 검증"
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

    for params in PARAM_SETS:
        print(
            "\n"
            + "="
            * 80
        )

        print(
            f"Params: "
            f"{params}"
        )

        print(
            "="
            * 80
        )

        fold_rows = []
        signal_frames = []

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
                unique_dates[
                    start
                ]
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
                    features
                ]
                .fillna(0)
            )

            y_train = (
                train_df[
                    "Target"
                ]
            )

            X_test = (
                test_df[
                    features
                ]
                .fillna(0)
            )

            y_test = (
                test_df[
                    "Target"
                ]
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

            model = (
                create_tuning_model(
                    params
                )
            )

            model.fit(
                X_train,
                y_train,
            )

            probabilities = (
                model.predict_proba(
                    X_test
                )[:, 1]
            )

            predictions = (
                probabilities
                >= threshold
            ).astype(int)

            accuracy = (
                accuracy_score(
                    y_test,
                    predictions,
                )
            )

            test_df[
                "Probability"
            ] = probabilities

            test_df[
                "Fold"
            ] = fold

            signal_df = test_df[
                test_df[
                    "Probability"
                ]
                >= threshold
            ].copy()

            if signal_df.empty:
                trade_count = 0
                success_rate = None
                profitable_rate = None
                avg_return = None
                median_return = None

                print(
                    f"Fold {fold} | "
                    "신호 없음 | "
                    f"정확도 "
                    f"{accuracy:.2%}"
                )

            else:
                returns = (
                    signal_df[
                        "Future_Return_5D"
                    ]
                    .astype(float)
                )

                trade_count = int(
                    len(signal_df)
                )

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

                avg_return = float(
                    returns.mean()
                )

                median_return = float(
                    returns.median()
                )

                signal_df[
                    "Subset_Name"
                ] = subset_name

                signal_df[
                    "Threshold"
                ] = threshold

                signal_df[
                    "Params"
                ] = str(
                    params
                )

                signal_frames.append(
                    signal_df
                )

                print(
                    f"Fold {fold} | "
                    f"신호 "
                    f"{trade_count}개 | "
                    f"+3% 성공률 "
                    f"{success_rate:.2%} | "
                    f"수익 발생률 "
                    f"{profitable_rate:.2%} | "
                    f"평균수익 "
                    f"{avg_return:.2%} | "
                    f"정확도 "
                    f"{accuracy:.2%}"
                )

            fold_rows.append({
                "params": str(
                    params
                ),
                "fold": fold,
                "accuracy": float(
                    accuracy
                ),
                "trade_count": int(
                    trade_count
                ),
                "success_rate_3pct": (
                    success_rate
                ),
                "profitable_rate": (
                    profitable_rate
                ),
                "avg_return_5d": (
                    avg_return
                ),
                "median_return_5d": (
                    median_return
                ),
            })

            fold += 1

        fold_df = pd.DataFrame(
            fold_rows
        )

        if fold_df.empty:
            print(
                "유효한 Fold가 없습니다."
            )
            continue

        if signal_frames:
            combined_signal_df = (
                pd.concat(
                    signal_frames,
                    ignore_index=True,
                )
            )

            combined_returns = (
                combined_signal_df[
                    "Future_Return_5D"
                ]
                .astype(float)
            )

            total_trades = int(
                len(
                    combined_signal_df
                )
            )

            overall_success_rate = float(
                (
                    combined_returns
                    >= 0.03
                ).mean()
            )

            overall_profitable_rate = float(
                (
                    combined_returns
                    > 0
                ).mean()
            )

            overall_avg_return = float(
                combined_returns.mean()
            )

            overall_median_return = float(
                combined_returns.median()
            )

            worst_return = float(
                combined_returns.min()
            )

            best_return = float(
                combined_returns.max()
            )

        else:
            total_trades = 0
            overall_success_rate = None
            overall_profitable_rate = None
            overall_avg_return = None
            overall_median_return = None
            worst_return = None
            best_return = None

        valid_signal_folds = fold_df[
            fold_df[
                "trade_count"
            ]
            > 0
        ]

        if valid_signal_folds.empty:
            avg_fold_success_rate = None
            avg_fold_return = None
        else:
            avg_fold_success_rate = float(
                valid_signal_folds[
                    "success_rate_3pct"
                ].mean()
            )

            avg_fold_return = float(
                valid_signal_folds[
                    "avg_return_5d"
                ].mean()
            )

        results.append({
            "subset_name": (
                subset_name
            ),
            "feature_count": int(
                len(features)
            ),
            "threshold": float(
                threshold
            ),
            "holding_days": int(
                holding_days
            ),
            "top_n_signals": int(
                top_n_signals
            ),
            "max_open_positions": int(
                max_open_positions
            ),
            "params": str(
                params
            ),
            "valid_fold_count": int(
                len(fold_df)
            ),
            "avg_accuracy": float(
                fold_df[
                    "accuracy"
                ].mean()
            ),
            "total_trades": int(
                total_trades
            ),
            "overall_success_rate_3pct": (
                overall_success_rate
            ),
            "overall_profitable_rate": (
                overall_profitable_rate
            ),
            "overall_avg_return_5d": (
                overall_avg_return
            ),
            "overall_median_return_5d": (
                overall_median_return
            ),
            "avg_fold_success_rate_3pct": (
                avg_fold_success_rate
            ),
            "avg_fold_return_5d": (
                avg_fold_return
            ),
            "worst_return": (
                worst_return
            ),
            "best_return": (
                best_return
            ),
        })

    result_df = pd.DataFrame(
        results
    )

    if result_df.empty:
        raise ValueError(
            "Hyperparameter Tuning 결과가 "
            "생성되지 않았습니다."
        )

    result_df = (
        result_df.sort_values(
            by=[
                "overall_avg_return_5d",
                "overall_success_rate_3pct",
                "total_trades",
                "avg_accuracy",
            ],
            ascending=[
                False,
                False,
                False,
                False,
            ],
            na_position="last",
        )
        .reset_index(
            drop=True
        )
    )

    result_df[
        "rank"
    ] = (
        result_df.index
        + 1
    )

    output_columns = [
        "rank",
        "subset_name",
        "feature_count",
        "threshold",
        "holding_days",
        "top_n_signals",
        "max_open_positions",
        "params",
        "valid_fold_count",
        "avg_accuracy",
        "total_trades",
        "overall_success_rate_3pct",
        "overall_profitable_rate",
        "overall_avg_return_5d",
        "overall_median_return_5d",
        "avg_fold_success_rate_3pct",
        "avg_fold_return_5d",
        "worst_return",
        "best_return",
    ]

    result_df = result_df[
        output_columns
    ]

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "Hyperparameter Tuning "
        "최종 결과"
    )

    print(
        "#"
        * 80
    )

    print(
        result_df.to_string(
            index=False
        )
    )

    result_df.to_csv(
        RESULT_PATH,
        index=False,
    )

    print(
        "\nCSV 저장 완료: "
        f"{RESULT_PATH}"
    )

    return result_df


if __name__ == "__main__":
    run_tuning()