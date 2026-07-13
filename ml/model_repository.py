import os
from datetime import (
    datetime,
)
from pathlib import (
    Path,
)

import joblib


ACTIVE_MODEL_PATH = Path(
    "ml/trained_model.pkl"
)

MODEL_STORE_DIR = Path(
    "ml/model_store"
)

CANDIDATE_DIR = (
    MODEL_STORE_DIR
    / "candidates"
)

FINAL_CANDIDATE_DIR = (
    MODEL_STORE_DIR
    / "final_candidates"
)

ARCHIVE_DIR = (
    MODEL_STORE_DIR
    / "archive"
)

EVALUATION_DIR = (
    MODEL_STORE_DIR
    / "evaluations"
)


REQUIRED_MODEL_KEYS = {
    "model",
    "subset_name",
    "features",
    "threshold",
    "holding_days",
    "top_n_signals",
    "max_open_positions",
}


def initialize_model_store():
    for directory in [
        MODEL_STORE_DIR,
        CANDIDATE_DIR,
        FINAL_CANDIDATE_DIR,
        ARCHIVE_DIR,
        EVALUATION_DIR,
    ]:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


def validate_model_data(
    model_data,
):
    if not isinstance(
        model_data,
        dict,
    ):
        raise ValueError(
            "저장된 모델 데이터는 "
            "dict 형식이어야 합니다."
        )

    missing_keys = (
        REQUIRED_MODEL_KEYS
        - set(
            model_data.keys()
        )
    )

    if missing_keys:
        raise ValueError(
            "모델 데이터에 필요한 "
            "항목이 없습니다: "
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
        raise ValueError(
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

    return True


def load_model_data(
    model_path=ACTIVE_MODEL_PATH,
):
    model_path = Path(
        model_path
    )

    if not model_path.exists():
        raise FileNotFoundError(
            "모델 파일이 없습니다: "
            f"{model_path}"
        )

    model_data = joblib.load(
        model_path
    )

    validate_model_data(
        model_data
    )

    return model_data


def save_model_data_atomic(
    model_data,
    model_path,
):
    validate_model_data(
        model_data
    )

    initialize_model_store()

    model_path = Path(
        model_path
    )

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = (
        model_path.with_suffix(
            model_path.suffix
            + ".tmp"
        )
    )

    joblib.dump(
        model_data,
        temporary_path,
    )

    os.replace(
        temporary_path,
        model_path,
    )

    return model_path


def create_candidate_model_path():
    initialize_model_store()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return (
        CANDIDATE_DIR
        / (
            "candidate_"
            f"{timestamp}.pkl"
        )
    )


def create_final_candidate_model_path(
    candidate_path,
):
    initialize_model_store()

    candidate_path = Path(
        candidate_path
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    candidate_name = (
        candidate_path.stem
    )

    return (
        FINAL_CANDIDATE_DIR
        / (
            f"{candidate_name}_"
            f"final_{timestamp}.pkl"
        )
    )


def create_archive_model_path(
    model_data,
):
    initialize_model_store()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    subset_name = str(
        model_data.get(
            "subset_name",
            "unknown",
        )
    )

    return (
        ARCHIVE_DIR
        / (
            "model_"
            f"{timestamp}_"
            f"{subset_name}.pkl"
        )
    )


def archive_active_model():
    active_model_data = (
        load_model_data(
            ACTIVE_MODEL_PATH
        )
    )

    archive_path = (
        create_archive_model_path(
            active_model_data
        )
    )

    save_model_data_atomic(
        model_data=active_model_data,
        model_path=archive_path,
    )

    return archive_path


def promote_candidate_model(
    candidate_path,
):
    candidate_path = Path(
        candidate_path
    )

    candidate_model_data = (
        load_model_data(
            candidate_path
        )
    )

    archive_path = None

    if ACTIVE_MODEL_PATH.exists():
        archive_path = (
            archive_active_model()
        )

    save_model_data_atomic(
        model_data=(
            candidate_model_data
        ),
        model_path=(
            ACTIVE_MODEL_PATH
        ),
    )

    return {
        "active_model_path": str(
            ACTIVE_MODEL_PATH
        ),
        "archive_model_path": (
            str(
                archive_path
            )
            if archive_path
            is not None
            else None
        ),
        "candidate_model_path": str(
            candidate_path
        ),
    }


def get_model_summary(
    model_data,
):
    validate_model_data(
        model_data
    )

    model = model_data[
        "model"
    ]

    return {
        "subset_name": (
            model_data[
                "subset_name"
            ]
        ),
        "feature_count": len(
            model_data[
                "features"
            ]
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
        "trained_at": (
            model_data.get(
                "trained_at"
            )
        ),
        "train_start_date": (
            model_data.get(
                "train_start_date"
            )
        ),
        "train_end_date": (
            model_data.get(
                "train_end_date"
            )
        ),
        "validation_start_date": (
            model_data.get(
                "validation_start_date"
            )
        ),
        "validation_end_date": (
            model_data.get(
                "validation_end_date"
            )
        ),
        "model_class": (
            model.__class__.__name__
        ),
        "model_params": (
            model_data.get(
                "model_params",
                model.get_params(),
            )
        ),
    }


if __name__ == "__main__":
    initialize_model_store()

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "ML 모델 저장소 확인"
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
        f"후보 모델 폴더: "
        f"{CANDIDATE_DIR}"
    )

    print(
        f"최종 후보 모델 폴더: "
        f"{FINAL_CANDIDATE_DIR}"
    )

    print(
        f"백업 모델 폴더: "
        f"{ARCHIVE_DIR}"
    )

    if (
        ACTIVE_MODEL_PATH.exists()
    ):
        model_data = (
            load_model_data(
                ACTIVE_MODEL_PATH
            )
        )

        summary = (
            get_model_summary(
                model_data
            )
        )

        for key, value in (
            summary.items()
        ):
            print(
                f"{key}: "
                f"{value}"
            )

    else:
        print(
            "현재 운영 모델이 없습니다."
        )