from pathlib import (
    Path,
)

import pandas as pd

from ml.feature_subset_trade_backtest import (
    HOLDING_DAYS,
    MAX_OPEN_POSITIONS,
    TOP_N_SIGNALS,
    add_exit_date,
    calculate_trade_metrics,
    select_non_overlapping_trades,
)
from ml.ml_model import (
    create_model,
)
from ml.model_repository import (
    ACTIVE_MODEL_PATH,
    load_model_data,
)
from ml.walk_forward import (
    DEFAULT_MINIMUM_WINDOW_COUNT,
    DEFAULT_PURGE_SIZE,
    DEFAULT_STEP_SIZE,
    DEFAULT_TRAIN_SIZE,
    DEFAULT_VALIDATION_SIZE,
    generate_walk_forward_windows,
    get_walk_forward_dataframes,
)


DATASET_PATH = Path(
    "ml/training_dataset.csv"
)


def validate_model_data_for_walk_forward(
    model_data,
):
    if not isinstance(
        model_data,
        dict,
    ):
        raise TypeError(
            "Walk Forward 모델 데이터는 "
            "dict 형식이어야 합니다."
        )

    required_keys = {
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
            "Walk Forward 모델 데이터에 "
            "필요한 항목이 없습니다: "
            + ", ".join(
                sorted(
                    missing_keys
                )
            )
        )

    features = model_data[
        "features"
    ]

    if not isinstance(
        features,
        list,
    ):
        raise TypeError(
            "모델 Feature는 "
            "list 형식이어야 합니다."
        )

    if not features:
        raise ValueError(
            "모델 Feature 목록이 "
            "비어 있습니다."
        )

    threshold = float(
        model_data[
            "threshold"
        ]
    )

    if not (
        0.0
        < threshold
        < 1.0
    ):
        raise ValueError(
            "모델 Threshold는 "
            "0과 1 사이여야 합니다."
        )

    model_params = (
        model_data.get(
            "model_params"
        )
    )

    if model_params is None:
        stored_model = (
            model_data.get(
                "model"
            )
        )

        if stored_model is None:
            raise ValueError(
                "Walk Forward 재학습에 사용할 "
                "모델 파라미터가 없습니다."
            )

        model_params = (
            stored_model.get_params()
        )

    if not isinstance(
        model_params,
        dict,
    ):
        raise TypeError(
            "저장된 모델 파라미터는 "
            "dict 형식이어야 합니다."
        )

    return True


def validate_walk_forward_trading_config(
    model_data,
):
    saved_config = {
        "holding_days": int(
            model_data[
                "holding_days"
            ]
        ),
        "top_n_signals": int(
            model_data[
                "top_n_signals"
            ]
        ),
        "max_open_positions": int(
            model_data[
                "max_open_positions"
            ]
        ),
    }

    runtime_config = {
        "holding_days": int(
            HOLDING_DAYS
        ),
        "top_n_signals": int(
            TOP_N_SIGNALS
        ),
        "max_open_positions": int(
            MAX_OPEN_POSITIONS
        ),
    }

    if (
        saved_config
        != runtime_config
    ):
        raise ValueError(
            "저장된 모델 거래 설정과 "
            "Walk Forward 백테스트 설정이 "
            "다릅니다. "
            f"저장 설정={saved_config}, "
            f"실행 설정={runtime_config}"
        )

    return True


def validate_walk_forward_dataset(
    df,
    features,
):
    if not isinstance(
        df,
        pd.DataFrame,
    ):
        raise TypeError(
            "Walk Forward 데이터셋은 "
            "DataFrame이어야 합니다."
        )

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
        - set(
            df.columns
        )
    )

    if missing_columns:
        raise ValueError(
            "Walk Forward 데이터셋에 "
            "필요한 컬럼이 없습니다: "
            + ", ".join(
                sorted(
                    missing_columns
                )
            )
        )

    if df.empty:
        raise ValueError(
            "Walk Forward 데이터셋이 "
            "비어 있습니다."
        )

    return True


def prepare_walk_forward_dataset(
    df,
):
    working_df = df.copy()

    working_df[
        "Date"
    ] = pd.to_datetime(
        working_df[
            "Date"
        ],
        errors="raise",
    )

    working_df = (
        working_df.sort_values(
            by=[
                "Date",
                "Ticker",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    return working_df


def get_model_params(
    model_data,
):
    model_params = (
        model_data.get(
            "model_params"
        )
    )

    if model_params is not None:
        return dict(
            model_params
        )

    return dict(
        model_data[
            "model"
        ].get_params()
    )


def get_positive_class_index(
    model,
):
    classes = list(
        model.classes_
    )

    if 1 not in classes:
        raise ValueError(
            "학습된 모델 클래스에 "
            "양성 클래스 1이 없습니다."
        )

    return classes.index(
        1
    )


def create_empty_window_metrics():
    return {
        "raw_signal_count": 0,
        "candidate_trade_count": 0,
        "trade_count": 0,
        "skipped_trade_count": 0,
        "success_rate_3pct": None,
        "profitable_rate": None,
        "average_return": None,
        "median_return": None,
        "return_std": None,
        "best_trade": None,
        "worst_trade": None,
        "total_return": 0.0,
        "final_money": 1_000_000.0,
        "max_drawdown": 0.0,
    }


def evaluate_walk_forward_window(
    model_data,
    train_df,
    validation_df,
    window,
):
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

    X_train = (
        train_df[
            features
        ]
        .fillna(0)
    )

    y_train = train_df[
        "Target"
    ]

    X_validation = (
        validation_df[
            features
        ]
        .fillna(0)
    )

    if X_train.empty:
        raise ValueError(
            "Walk Forward 학습 데이터가 "
            "비어 있습니다. "
            f"Window={window.window_number}"
        )

    if X_validation.empty:
        raise ValueError(
            "Walk Forward 검증 데이터가 "
            "비어 있습니다. "
            f"Window={window.window_number}"
        )

    if (
        y_train.nunique()
        < 2
    ):
        raise ValueError(
            "Walk Forward 학습 Target 클래스가 "
            "2개 미만입니다. "
            f"Window={window.window_number}"
        )

    model = create_model(
        model_params=(
            get_model_params(
                model_data
            )
        )
    )

    model.fit(
        X_train,
        y_train,
    )

    positive_class_index = (
        get_positive_class_index(
            model
        )
    )

    probabilities = (
        model.predict_proba(
            X_validation
        )[
            :,
            positive_class_index,
        ]
    )

    prediction_df = (
        validation_df.copy()
    )

    prediction_df[
        "Probability"
    ] = probabilities

    prediction_df[
        "Signal"
    ] = (
        prediction_df[
            "Probability"
        ]
        >= threshold
    )

    prediction_df[
        "Window_Number"
    ] = int(
        window.window_number
    )

    raw_signal_df = prediction_df[
        prediction_df[
            "Signal"
        ]
        == True
    ].copy()

    if raw_signal_df.empty:
        metrics = (
            create_empty_window_metrics()
        )

        selected_trade_df = (
            pd.DataFrame()
        )

    else:
        selected_trade_df = (
            select_non_overlapping_trades(
                raw_signal_df
            )
        )

        selected_trade_df = (
            add_exit_date(
                selected_trade_df
            )
        )

        metrics = (
            calculate_trade_metrics(
                selected_trade_df
            )
        )

        metrics = {
            "raw_signal_count": int(
                len(
                    raw_signal_df
                )
            ),
            **metrics,
        }

    window_result = {
        **window.to_dict(),
        "train_row_count": int(
            len(
                train_df
            )
        ),
        "validation_row_count": int(
            len(
                validation_df
            )
        ),
        "train_target_positive_count": int(
            y_train.sum()
        ),
        "train_target_positive_rate": float(
            y_train.mean()
        ),
        "validation_target_positive_count": int(
            validation_df[
                "Target"
            ].sum()
        ),
        "validation_target_positive_rate": float(
            validation_df[
                "Target"
            ].mean()
        ),
        "metrics": (
            metrics
        ),
    }

    return {
        "window_result": (
            window_result
        ),
        "raw_signal_df": (
            raw_signal_df
        ),
        "selected_trade_df": (
            selected_trade_df
        ),
    }


def calculate_window_summary(
    window_results,
):
    if not window_results:
        raise ValueError(
            "집계할 Walk Forward "
            "Window 결과가 없습니다."
        )

    total_returns = pd.Series(
        [
            float(
                result[
                    "metrics"
                ][
                    "total_return"
                ]
            )
            for result
            in window_results
        ],
        dtype=float,
    )

    trade_counts = pd.Series(
        [
            int(
                result[
                    "metrics"
                ][
                    "trade_count"
                ]
            )
            for result
            in window_results
        ],
        dtype=int,
    )

    positive_window_count = int(
        (
            total_returns
            > 0
        ).sum()
    )

    non_negative_window_count = int(
        (
            total_returns
            >= 0
        ).sum()
    )

    return {
        "window_count": int(
            len(
                window_results
            )
        ),
        "positive_window_count": (
            positive_window_count
        ),
        "non_negative_window_count": (
            non_negative_window_count
        ),
        "positive_window_ratio": float(
            positive_window_count
            / len(
                window_results
            )
        ),
        "non_negative_window_ratio": float(
            non_negative_window_count
            / len(
                window_results
            )
        ),
        "average_window_total_return": float(
            total_returns.mean()
        ),
        "median_window_total_return": float(
            total_returns.median()
        ),
        "window_total_return_std": float(
            total_returns.std(
                ddof=0
            )
        ),
        "best_window_total_return": float(
            total_returns.max()
        ),
        "worst_window_total_return": float(
            total_returns.min()
        ),
        "total_window_trade_count": int(
            trade_counts.sum()
        ),
        "average_window_trade_count": float(
            trade_counts.mean()
        ),
        "minimum_window_trade_count": int(
            trade_counts.min()
        ),
        "maximum_window_trade_count": int(
            trade_counts.max()
        ),
    }


def calculate_aggregate_metrics(
    raw_signal_frames,
):
    if not raw_signal_frames:
        return {
            **create_empty_window_metrics(),
            "validation_start_date": None,
            "validation_end_date": None,
        }

    all_raw_signals = (
        pd.concat(
            raw_signal_frames,
            ignore_index=True,
        )
    )

    all_raw_signals = (
        all_raw_signals.sort_values(
            by=[
                "Date",
                "Probability",
                "Ticker",
            ],
            ascending=[
                True,
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    duplicate_signal_mask = (
        all_raw_signals.duplicated(
            subset=[
                "Date",
                "Ticker",
            ],
            keep=False,
        )
    )

    if (
        duplicate_signal_mask.any()
    ):
        duplicate_signals = (
            all_raw_signals[
                duplicate_signal_mask
            ][
                [
                    "Date",
                    "Ticker",
                    "Window_Number",
                ]
            ]
        )

        raise ValueError(
            "Walk Forward 검증 구간에 "
            "중복 종목 신호가 존재합니다. "
            "Validation Window가 겹치는지 "
            "확인해야 합니다. "
            f"중복 수={len(duplicate_signals)}"
        )

    selected_trade_df = (
        select_non_overlapping_trades(
            all_raw_signals
        )
    )

    selected_trade_df = (
        add_exit_date(
            selected_trade_df
        )
    )

    metrics = (
        calculate_trade_metrics(
            selected_trade_df
        )
    )

    aggregate_metrics = {
        "raw_signal_count": int(
            len(
                all_raw_signals
            )
        ),
        **metrics,
        "validation_start_date": str(
            all_raw_signals[
                "Date"
            ]
            .min()
            .date()
        ),
        "validation_end_date": str(
            all_raw_signals[
                "Date"
            ]
            .max()
            .date()
        ),
    }

    return aggregate_metrics


def print_window_result(
    window_result,
):
    metrics = window_result[
        "metrics"
    ]

    print(
        "\n"
        + "-"
        * 80
    )

    print(
        f"Window "
        f"{window_result['window_number']}"
    )

    print(
        "-"
        * 80
    )

    print(
        "학습 기간: "
        f"{window_result['train_start_date']} "
        f"~ "
        f"{window_result['train_end_date']}"
    )

    print(
        "Purge 기간: "
        f"{window_result['purge_start_date']} "
        f"~ "
        f"{window_result['purge_end_date']}"
    )

    print(
        "검증 기간: "
        f"{window_result['validation_start_date']} "
        f"~ "
        f"{window_result['validation_end_date']}"
    )

    print(
        f"학습 행 수: "
        f"{window_result['train_row_count']:,}"
    )

    print(
        f"검증 행 수: "
        f"{window_result['validation_row_count']:,}"
    )

    print(
        f"원시 신호 수: "
        f"{metrics['raw_signal_count']:,}"
    )

    print(
        f"실제 거래 수: "
        f"{metrics['trade_count']:,}"
    )

    if (
        metrics[
            "trade_count"
        ]
        <= 0
    ):
        print(
            "실제 거래가 없습니다."
        )

        return

    print(
        f"+3% 성공률: "
        f"{metrics['success_rate_3pct']:.2%}"
    )

    print(
        f"평균 거래 순수익률: "
        f"{metrics['average_return']:.2%}"
    )

    print(
        f"누적 수익률: "
        f"{metrics['total_return']:.2%}"
    )

    print(
        f"최대 낙폭: "
        f"{metrics['max_drawdown']:.2%}"
    )


def print_walk_forward_evaluation(
    result,
):
    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "Walk Forward 모델 평가"
    )

    print(
        "#"
        * 80
    )

    print(
        f"Feature Subset: "
        f"{result['subset_name']}"
    )

    print(
        f"Feature 수: "
        f"{result['feature_count']}"
    )

    print(
        f"Threshold: "
        f"{result['threshold']:.2f}"
    )

    print(
        f"Window 수: "
        f"{result['window_count']}"
    )

    for window_result in (
        result[
            "window_results"
        ]
    ):
        print_window_result(
            window_result
        )

    window_summary = result[
        "window_summary"
    ]

    aggregate_metrics = result[
        "aggregate_metrics"
    ]

    print(
        "\n"
        + "="
        * 80
    )

    print(
        "Walk Forward 전체 요약"
    )

    print(
        "="
        * 80
    )

    print(
        "양수 수익 Window: "
        f"{window_summary['positive_window_count']} "
        f"/ "
        f"{window_summary['window_count']} "
        f"("
        f"{window_summary['positive_window_ratio']:.2%}"
        f")"
    )

    print(
        "평균 Window 수익률: "
        f"{window_summary['average_window_total_return']:.2%}"
    )

    print(
        "최악 Window 수익률: "
        f"{window_summary['worst_window_total_return']:.2%}"
    )

    print(
        "Window 수익률 표준편차: "
        f"{window_summary['window_total_return_std']:.2%}"
    )

    print(
        f"전체 OOS 원시 신호 수: "
        f"{aggregate_metrics['raw_signal_count']:,}"
    )

    print(
        f"전체 OOS 실제 거래 수: "
        f"{aggregate_metrics['trade_count']:,}"
    )

    if (
        aggregate_metrics[
            "trade_count"
        ]
        > 0
    ):
        print(
            "전체 OOS +3% 성공률: "
            f"{aggregate_metrics['success_rate_3pct']:.2%}"
        )

        print(
            "전체 OOS 평균 거래 순수익률: "
            f"{aggregate_metrics['average_return']:.2%}"
        )

        print(
            "전체 OOS 누적 수익률: "
            f"{aggregate_metrics['total_return']:.2%}"
        )

        print(
            "전체 OOS 최대 낙폭: "
            f"{aggregate_metrics['max_drawdown']:.2%}"
        )


def evaluate_model_walk_forward(
    model_data,
    df,
    train_size=DEFAULT_TRAIN_SIZE,
    validation_size=(
        DEFAULT_VALIDATION_SIZE
    ),
    step_size=DEFAULT_STEP_SIZE,
    purge_size=DEFAULT_PURGE_SIZE,
    minimum_window_count=(
        DEFAULT_MINIMUM_WINDOW_COUNT
    ),
    print_result=True,
):
    validate_model_data_for_walk_forward(
        model_data
    )

    validate_walk_forward_trading_config(
        model_data
    )

    features = list(
        model_data[
            "features"
        ]
    )

    validate_walk_forward_dataset(
        df=df,
        features=features,
    )

    working_df = (
        prepare_walk_forward_dataset(
            df
        )
    )

    windows = (
        generate_walk_forward_windows(
            dates=working_df[
                "Date"
            ],
            train_size=train_size,
            validation_size=(
                validation_size
            ),
            step_size=step_size,
            purge_size=purge_size,
            minimum_window_count=(
                minimum_window_count
            ),
        )
    )

    window_results = []

    raw_signal_frames = []

    for window in windows:
        train_df, (
            validation_df
        ) = (
            get_walk_forward_dataframes(
                df=working_df,
                window=window,
            )
        )

        evaluation = (
            evaluate_walk_forward_window(
                model_data=(
                    model_data
                ),
                train_df=train_df,
                validation_df=(
                    validation_df
                ),
                window=window,
            )
        )

        window_results.append(
            evaluation[
                "window_result"
            ]
        )

        raw_signal_df = (
            evaluation[
                "raw_signal_df"
            ]
        )

        if not raw_signal_df.empty:
            raw_signal_frames.append(
                raw_signal_df
            )

    window_summary = (
        calculate_window_summary(
            window_results
        )
    )

    aggregate_metrics = (
        calculate_aggregate_metrics(
            raw_signal_frames
        )
    )

    result = {
        "evaluation_method": (
            "rolling_walk_forward"
        ),
        "subset_name": (
            model_data[
                "subset_name"
            ]
        ),
        "features": list(
            features
        ),
        "feature_count": int(
            len(
                features
            )
        ),
        "threshold": float(
            model_data[
                "threshold"
            ]
        ),
        "holding_days": int(
            model_data[
                "holding_days"
            ]
        ),
        "top_n_signals": int(
            model_data[
                "top_n_signals"
            ]
        ),
        "max_open_positions": int(
            model_data[
                "max_open_positions"
            ]
        ),
        "model_params": (
            get_model_params(
                model_data
            )
        ),
        "train_size": int(
            train_size
        ),
        "validation_size": int(
            validation_size
        ),
        "step_size": int(
            step_size
        ),
        "purge_size": int(
            purge_size
        ),
        "minimum_window_count": int(
            minimum_window_count
        ),
        "window_count": int(
            len(
                windows
            )
        ),
        "window_results": (
            window_results
        ),
        "window_summary": (
            window_summary
        ),
        "aggregate_metrics": (
            aggregate_metrics
        ),
    }

    if print_result:
        print_walk_forward_evaluation(
            result
        )

    return result


def evaluate_saved_model_walk_forward(
    model_path=ACTIVE_MODEL_PATH,
    dataset_path=DATASET_PATH,
    print_result=True,
):
    model_data = (
        load_model_data(
            model_path
        )
    )

    df = pd.read_csv(
        dataset_path
    )

    return evaluate_model_walk_forward(
        model_data=model_data,
        df=df,
        print_result=print_result,
    )


if __name__ == "__main__":
    evaluate_saved_model_walk_forward()
