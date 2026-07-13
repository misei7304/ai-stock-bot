import argparse
import json
import os

from datetime import (
    datetime,
)
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
from ml.model_repository import (
    ACTIVE_MODEL_PATH,
    CANDIDATE_DIR,
    EVALUATION_DIR,
    get_model_summary,
    initialize_model_store,
    load_model_data,
    promote_candidate_model,
)
from ml.walk_forward_evaluator import (
    evaluate_model_walk_forward,
)


DATASET_PATH = Path(
    "ml/training_dataset.csv"
)

MINIMUM_TRADE_COUNT = 10

MINIMUM_TOTAL_RETURN_IMPROVEMENT = 0.02


def find_latest_candidate_model():
    initialize_model_store()

    candidate_paths = list(
        CANDIDATE_DIR.glob(
            "candidate_*.pkl"
        )
    )

    if not candidate_paths:
        raise FileNotFoundError(
            "평가할 후보 모델이 없습니다: "
            f"{CANDIDATE_DIR}"
        )

    candidate_paths = sorted(
        candidate_paths,
        key=lambda path: (
            path.stat().st_mtime,
            path.name,
        ),
    )

    return candidate_paths[-1]


def validate_dataset(
    df,
    active_features,
    candidate_features,
):
    required_columns = {
        "Date",
        "Ticker",
        "Close",
        "Future_Return_5D",
        "Target",
        *active_features,
        *candidate_features,
    }

    missing_columns = (
        required_columns
        - set(
            df.columns
        )
    )

    if missing_columns:
        raise ValueError(
            "모델 평가 데이터에 필요한 "
            "컬럼이 없습니다: "
            + ", ".join(
                sorted(
                    missing_columns
                )
            )
        )


def validate_trading_config(
    active_model_data,
    candidate_model_data,
):
    config_keys = [
        "holding_days",
        "top_n_signals",
        "max_open_positions",
    ]

    differences = []

    for key in config_keys:
        active_value = (
            active_model_data[
                key
            ]
        )

        candidate_value = (
            candidate_model_data[
                key
            ]
        )

        if (
            active_value
            != candidate_value
        ):
            differences.append(
                f"{key}: "
                f"active={active_value}, "
                f"candidate={candidate_value}"
            )

    if differences:
        raise ValueError(
            "운영 모델과 후보 모델의 "
            "거래 설정이 다릅니다: "
            + " | ".join(
                differences
            )
        )

    holding_days = int(
        active_model_data[
            "holding_days"
        ]
    )

    top_n_signals = int(
        active_model_data[
            "top_n_signals"
        ]
    )

    max_open_positions = int(
        active_model_data[
            "max_open_positions"
        ]
    )

    runtime_config = {
        "holding_days": (
            HOLDING_DAYS
        ),
        "top_n_signals": (
            TOP_N_SIGNALS
        ),
        "max_open_positions": (
            MAX_OPEN_POSITIONS
        ),
    }

    saved_config = {
        "holding_days": (
            holding_days
        ),
        "top_n_signals": (
            top_n_signals
        ),
        "max_open_positions": (
            max_open_positions
        ),
    }

    if (
        runtime_config
        != saved_config
    ):
        raise ValueError(
            "저장된 모델 거래 설정과 "
            "백테스트 실행 설정이 다릅니다. "
            f"저장 설정={saved_config}, "
            f"실행 설정={runtime_config}"
        )


def get_validation_dataframe(
    df,
):
    unique_dates = sorted(
        df[
            "Date"
        ].unique()
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
            "모델 평가용 검증 구간을 "
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
            "모델 평가용 검증 데이터가 "
            "없습니다."
        )

    return validation_df


def get_positive_class_index(
    model,
):
    classes = list(
        model.classes_
    )

    if 1 not in classes:
        raise ValueError(
            "모델 클래스에 양성 클래스 1이 "
            "존재하지 않습니다."
        )

    return classes.index(
        1
    )


def evaluate_single_model(
    model_data,
    validation_df,
):
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

    missing_features = [
        feature
        for feature in features
        if feature
        not in validation_df.columns
    ]

    if missing_features:
        raise ValueError(
            "검증 데이터에 모델 Feature가 "
            "없습니다: "
            + ", ".join(
                missing_features
            )
        )

    X_validation = (
        validation_df[
            features
        ]
        .fillna(0)
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

    raw_signal_df = prediction_df[
        prediction_df[
            "Signal"
        ]
        == True
    ].copy()

    if raw_signal_df.empty:
        return {
            "subset_name": (
                model_data[
                    "subset_name"
                ]
            ),
            "feature_count": len(
                features
            ),
            "threshold": (
                threshold
            ),
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

    return {
        "subset_name": (
            model_data[
                "subset_name"
            ]
        ),
        "feature_count": len(
            features
        ),
        "threshold": (
            threshold
        ),
        "raw_signal_count": int(
            len(
                raw_signal_df
            )
        ),
        **metrics,
    }


def get_metric_value(
    metrics,
    key,
    default_value,
):
    value = metrics.get(
        key
    )

    if value is None:
        return default_value

    return float(
        value
    )


def decide_promotion(
    active_metrics,
    candidate_metrics,
):
    active_total_return = (
        get_metric_value(
            active_metrics,
            "total_return",
            0.0,
        )
    )

    candidate_total_return = (
        get_metric_value(
            candidate_metrics,
            "total_return",
            0.0,
        )
    )

    active_success_rate = (
        get_metric_value(
            active_metrics,
            "success_rate_3pct",
            0.0,
        )
    )

    candidate_success_rate = (
        get_metric_value(
            candidate_metrics,
            "success_rate_3pct",
            0.0,
        )
    )

    active_average_return = (
        get_metric_value(
            active_metrics,
            "average_return",
            0.0,
        )
    )

    candidate_average_return = (
        get_metric_value(
            candidate_metrics,
            "average_return",
            0.0,
        )
    )

    active_max_drawdown = (
        get_metric_value(
            active_metrics,
            "max_drawdown",
            -1.0,
        )
    )

    candidate_max_drawdown = (
        get_metric_value(
            candidate_metrics,
            "max_drawdown",
            -1.0,
        )
    )

    active_worst_trade = (
        get_metric_value(
            active_metrics,
            "worst_trade",
            -1.0,
        )
    )

    candidate_worst_trade = (
        get_metric_value(
            candidate_metrics,
            "worst_trade",
            -1.0,
        )
    )

    candidate_trade_count = int(
        candidate_metrics.get(
            "trade_count",
            0,
        )
    )

    total_return_improvement = (
        candidate_total_return
        - active_total_return
    )

    conditions = {
        "minimum_trade_count": (
            candidate_trade_count
            >= MINIMUM_TRADE_COUNT
        ),
        "total_return_improved": (
            total_return_improvement
            >= MINIMUM_TOTAL_RETURN_IMPROVEMENT
        ),
        "success_rate_not_lower": (
            candidate_success_rate
            >= active_success_rate
        ),
        "average_return_not_lower": (
            candidate_average_return
            >= active_average_return
        ),
        "max_drawdown_not_worse": (
            candidate_max_drawdown
            >= active_max_drawdown
        ),
        "worst_trade_not_worse": (
            candidate_worst_trade
            >= active_worst_trade
        ),
    }

    approved = all(
        conditions.values()
    )

    failed_conditions = [
        condition_name
        for (
            condition_name,
            passed,
        )
        in conditions.items()
        if not passed
    ]

    return {
        "approved": bool(
            approved
        ),
        "conditions": (
            conditions
        ),
        "failed_conditions": (
            failed_conditions
        ),
        "minimum_trade_count": (
            MINIMUM_TRADE_COUNT
        ),
        "minimum_total_return_improvement": (
            MINIMUM_TOTAL_RETURN_IMPROVEMENT
        ),
        "total_return_improvement": float(
            total_return_improvement
        ),
    }


def make_json_serializable(
    value,
):
    if isinstance(
        value,
        dict,
    ):
        return {
            str(key): (
                make_json_serializable(
                    item
                )
            )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        list,
    ):
        return [
            make_json_serializable(
                item
            )
            for item in value
        ]

    if isinstance(
        value,
        tuple,
    ):
        return [
            make_json_serializable(
                item
            )
            for item in value
        ]

    if isinstance(
        value,
        Path,
    ):
        return str(
            value
        )

    if isinstance(
        value,
        pd.Timestamp,
    ):
        return value.isoformat()

    if hasattr(
        value,
        "item",
    ):
        try:
            return value.item()
        except (
            ValueError,
            TypeError,
        ):
            pass

    return value


def save_evaluation_result(
    evaluation_result,
):
    initialize_model_store()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    evaluation_path = (
        EVALUATION_DIR
        / (
            "evaluation_"
            f"{timestamp}.json"
        )
    )

    temporary_path = (
        evaluation_path.with_suffix(
            ".json.tmp"
        )
    )

    serializable_result = (
        make_json_serializable(
            evaluation_result
        )
    )

    with temporary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            serializable_result,
            file,
            ensure_ascii=False,
            indent=2,
        )

    os.replace(
        temporary_path,
        evaluation_path,
    )

    return evaluation_path


def print_model_metrics(
    title,
    metrics,
):
    print(
        "\n"
        + "-"
        * 80
    )

    print(
        title
    )

    print(
        "-"
        * 80
    )

    print(
        f"Feature Subset: "
        f"{metrics['subset_name']}"
    )

    print(
        f"Feature 수: "
        f"{metrics['feature_count']}"
    )

    print(
        f"Threshold: "
        f"{metrics['threshold']:.2f}"
    )

    print(
        f"원시 신호 수: "
        f"{metrics['raw_signal_count']:,}"
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
        <= 0
    ):
        print(
            "실제 체결 거래가 없습니다."
        )

        return

    print(
        f"+3% 성공률: "
        f"{metrics['success_rate_3pct']:.2%}"
    )

    print(
        f"수익 발생률: "
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


def evaluate_candidate_model(
    candidate_path=None,
    promote=False,
):
    initialize_model_store()

    if candidate_path is None:
        candidate_path = (
            find_latest_candidate_model()
        )

    candidate_path = Path(
        candidate_path
    )

    active_model_data = (
        load_model_data(
            ACTIVE_MODEL_PATH
        )
    )

    candidate_model_data = (
        load_model_data(
            candidate_path
        )
    )

    validate_trading_config(
        active_model_data=(
            active_model_data
        ),
        candidate_model_data=(
            candidate_model_data
        ),
    )

    active_features = list(
        active_model_data[
            "features"
        ]
    )

    candidate_features = list(
        candidate_model_data[
            "features"
        ]
    )

    df = pd.read_csv(
        DATASET_PATH
    )

    validate_dataset(
        df=df,
        active_features=(
            active_features
        ),
        candidate_features=(
            candidate_features
        ),
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

    active_metrics = (
        evaluate_single_model(
            model_data=(
                active_model_data
            ),
            validation_df=(
                validation_df
            ),
        )
    )

    candidate_metrics = (
        evaluate_single_model(
            model_data=(
                candidate_model_data
            ),
            validation_df=(
                validation_df
            ),
        )
    )

    print(
        "\n4. 운영 모델 Walk Forward 평가"
    )

    active_walk_forward_result = (
        evaluate_model_walk_forward(
            model_data=(
                active_model_data
            ),
            df=df,
            print_result=False,
        )
    )

    print(
        "운영 모델 Walk Forward 평가 완료"
    )

    print(
        "\n5. 후보 모델 Walk Forward 평가"
    )

    candidate_walk_forward_result = (
        evaluate_model_walk_forward(
            model_data=(
                candidate_model_data
            ),
            df=df,
            print_result=False,
        )
    )

    print(
        "후보 모델 Walk Forward 평가 완료"
    )

    promotion_decision = (
        decide_promotion(
            active_metrics=(
                active_metrics
            ),
            candidate_metrics=(
                candidate_metrics
            ),
        )
    )

    evaluation_result = {
        "evaluation_method": (
            "holdout_and_walk_forward"
        ),
        "evaluated_at": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        ),
        "validation_start_date": str(
            validation_df[
                "Date"
            ]
            .min()
            .date()
        ),
        "validation_end_date": str(
            validation_df[
                "Date"
            ]
            .max()
            .date()
        ),
        "validation_row_count": int(
            len(
                validation_df
            )
        ),
        "active_model_path": str(
            ACTIVE_MODEL_PATH
        ),
        "candidate_model_path": str(
            candidate_path
        ),
        "active_model_summary": (
            get_model_summary(
                active_model_data
            )
        ),
        "candidate_model_summary": (
            get_model_summary(
                candidate_model_data
            )
        ),
        "active_metrics": (
            active_metrics
        ),
        "candidate_metrics": (
            candidate_metrics
        ),
        "active_walk_forward": (
            active_walk_forward_result
        ),
        "candidate_walk_forward": (
            candidate_walk_forward_result
        ),
        "promotion_decision": (
            promotion_decision
        ),
        "promotion_requested": bool(
            promote
        ),
        "promotion_executed": False,
        "promotion_result": None,
    }

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "운영 모델과 후보 모델 비교 평가"
    )

    print(
        "#"
        * 80
    )

    print(
        f"운영 모델: "
        f"{ACTIVE_MODEL_PATH}"
    )

    print(
        f"후보 모델: "
        f"{candidate_path}"
    )

    print(
        f"검증 기간: "
        f"{evaluation_result['validation_start_date']} "
        f"~ "
        f"{evaluation_result['validation_end_date']}"
    )

    print(
        f"검증 데이터 수: "
        f"{evaluation_result['validation_row_count']:,}"
    )

    print_model_metrics(
        title="운영 모델 평가",
        metrics=active_metrics,
    )

    print_model_metrics(
        title="후보 모델 평가",
        metrics=candidate_metrics,
    )

    active_walk_forward_summary = (
        active_walk_forward_result[
            "window_summary"
        ]
    )

    candidate_walk_forward_summary = (
        candidate_walk_forward_result[
            "window_summary"
        ]
    )

    active_walk_forward_metrics = (
        active_walk_forward_result[
            "aggregate_metrics"
        ]
    )

    candidate_walk_forward_metrics = (
        candidate_walk_forward_result[
            "aggregate_metrics"
        ]
    )

    print(
        "\n"
        + "-"
        * 80
    )

    print(
        "Walk Forward 비교 요약"
    )

    print(
        "-"
        * 80
    )

    print(
        "운영 모델 양수 Window 비율: "
        f"{active_walk_forward_summary['positive_window_ratio']:.2%}"
    )

    print(
        "후보 모델 양수 Window 비율: "
        f"{candidate_walk_forward_summary['positive_window_ratio']:.2%}"
    )

    print(
        "운영 모델 최악 Window 수익률: "
        f"{active_walk_forward_summary['worst_window_total_return']:.2%}"
    )

    print(
        "후보 모델 최악 Window 수익률: "
        f"{candidate_walk_forward_summary['worst_window_total_return']:.2%}"
    )

    print(
        "운영 모델 전체 OOS 거래 수: "
        f"{active_walk_forward_metrics['trade_count']:,}"
    )

    print(
        "후보 모델 전체 OOS 거래 수: "
        f"{candidate_walk_forward_metrics['trade_count']:,}"
    )

    print(
        "운영 모델 전체 OOS 누적 수익률: "
        f"{active_walk_forward_metrics['total_return']:.2%}"
    )

    print(
        "후보 모델 전체 OOS 누적 수익률: "
        f"{candidate_walk_forward_metrics['total_return']:.2%}"
    )

    print(
        "운영 모델 전체 OOS 최대 낙폭: "
        f"{active_walk_forward_metrics['max_drawdown']:.2%}"
    )

    print(
        "후보 모델 전체 OOS 최대 낙폭: "
        f"{candidate_walk_forward_metrics['max_drawdown']:.2%}"
    )

    print(
        "\n"
        + "="
        * 80
    )

    print(
        "승격 판단"
    )

    print(
        "="
        * 80
    )

    for (
        condition_name,
        passed,
    ) in (
        promotion_decision[
            "conditions"
        ].items()
    ):
        print(
            f"{condition_name}: "
            f"{passed}"
        )

    print(
        "누적 수익률 개선 폭: "
        f"{promotion_decision['total_return_improvement']:.2%}"
    )

    if (
        promotion_decision[
            "approved"
        ]
    ):
        print(
            "판단: 후보 모델 승격 가능"
        )

    else:
        print(
            "판단: 후보 모델 승격 거부"
        )

        print(
            "실패 조건: "
            + ", ".join(
                promotion_decision[
                    "failed_conditions"
                ]
            )
        )

    if promote:
        if (
            promotion_decision[
                "approved"
            ]
        ):
            promotion_result = (
                promote_candidate_model(
                    candidate_path
                )
            )

            evaluation_result[
                "promotion_executed"
            ] = True

            evaluation_result[
                "promotion_result"
            ] = promotion_result

            print(
                "\n후보 모델 승격 완료"
            )

            print(
                "기존 운영 모델 백업: "
                f"{promotion_result['archive_model_path']}"
            )

            print(
                "새 운영 모델: "
                f"{promotion_result['active_model_path']}"
            )

        else:
            print(
                "\n승격 조건을 통과하지 않아 "
                "운영 모델을 변경하지 않습니다."
            )

    evaluation_path = (
        save_evaluation_result(
            evaluation_result
        )
    )

    print(
        "\n평가 결과 저장 완료: "
        f"{evaluation_path}"
    )

    return evaluation_result


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "운영 모델과 후보 모델을 "
            "동일한 검증 데이터로 비교합니다."
        )
    )

    parser.add_argument(
        "--candidate-path",
        type=str,
        default=None,
        help=(
            "평가할 후보 모델 경로. "
            "생략하면 최신 후보를 사용합니다."
        ),
    )

    parser.add_argument(
        "--promote",
        action="store_true",
        help=(
            "승격 조건을 통과한 경우 "
            "후보 모델을 운영 모델로 승격합니다."
        ),
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    evaluate_candidate_model(
        candidate_path=(
            args.candidate_path
        ),
        promote=(
            args.promote
        ),
    )