from ml.feature_subset_backtest import (
    FEATURE_SUBSETS,
)


SELECTED_SUBSET_NAME = (
    "core_plus_ma60_ratio"
)

SELECTED_FEATURES = list(
    FEATURE_SUBSETS[
        SELECTED_SUBSET_NAME
    ]
)

SELECTED_THRESHOLD = 0.70

SELECTED_HOLDING_DAYS = 5

SELECTED_TOP_N_SIGNALS = 3

SELECTED_MAX_OPEN_POSITIONS = 3


def validate_selected_model_config():
    if (
        SELECTED_SUBSET_NAME
        not in FEATURE_SUBSETS
    ):
        raise ValueError(
            "선택된 Feature Subset이 "
            "존재하지 않습니다: "
            f"{SELECTED_SUBSET_NAME}"
        )

    if not SELECTED_FEATURES:
        raise ValueError(
            "선택된 Feature 목록이 "
            "비어 있습니다."
        )

    expected_features = (
        FEATURE_SUBSETS[
            SELECTED_SUBSET_NAME
        ]
    )

    if (
        SELECTED_FEATURES
        != expected_features
    ):
        raise ValueError(
            "선택된 Feature 목록이 "
            "Feature Subset 정의와 "
            "일치하지 않습니다."
        )

    if not (
        0.0
        < SELECTED_THRESHOLD
        < 1.0
    ):
        raise ValueError(
            "선택된 Threshold는 "
            "0과 1 사이여야 합니다."
        )

    if (
        SELECTED_HOLDING_DAYS
        <= 0
    ):
        raise ValueError(
            "보유 기간은 "
            "1일 이상이어야 합니다."
        )

    if (
        SELECTED_TOP_N_SIGNALS
        <= 0
    ):
        raise ValueError(
            "일일 선택 신호 수는 "
            "1개 이상이어야 합니다."
        )

    if (
        SELECTED_MAX_OPEN_POSITIONS
        <= 0
    ):
        raise ValueError(
            "최대 보유 종목 수는 "
            "1개 이상이어야 합니다."
        )

    if (
        SELECTED_TOP_N_SIGNALS
        > SELECTED_MAX_OPEN_POSITIONS
    ):
        raise ValueError(
            "일일 선택 신호 수는 "
            "최대 보유 종목 수보다 "
            "클 수 없습니다."
        )

    return True


def get_selected_model_config():
    validate_selected_model_config()

    return {
        "subset_name": (
            SELECTED_SUBSET_NAME
        ),
        "features": list(
            SELECTED_FEATURES
        ),
        "threshold": (
            SELECTED_THRESHOLD
        ),
        "holding_days": (
            SELECTED_HOLDING_DAYS
        ),
        "top_n_signals": (
            SELECTED_TOP_N_SIGNALS
        ),
        "max_open_positions": (
            SELECTED_MAX_OPEN_POSITIONS
        ),
    }


if __name__ == "__main__":
    config = (
        get_selected_model_config()
    )

    print("\n" + "#" * 80)
    print("선택된 ML 모델 설정")
    print("#" * 80)

    print(
        f"Feature Subset: "
        f"{config['subset_name']}"
    )

    print(
        f"Feature 수: "
        f"{len(config['features'])}"
    )

    print(
        "Features: "
        + ", ".join(
            config["features"]
        )
    )

    print(
        f"Threshold: "
        f"{config['threshold']:.2f}"
    )

    print(
        f"Holding Days: "
        f"{config['holding_days']}"
    )

    print(
        f"Top N Signals: "
        f"{config['top_n_signals']}"
    )

    print(
        f"Max Open Positions: "
        f"{config['max_open_positions']}"
    )