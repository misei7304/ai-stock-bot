import argparse

from datetime import (
    datetime,
)
from pathlib import (
    Path,
)

import pandas as pd

from ml.ml_model import (
    create_model,
)
from ml.model_repository import (
    load_model_data,
    save_model_data_atomic,
)


DATASET_PATH = Path(
    "ml/training_dataset.csv"
)


def validate_final_training_dataset(
    df,
    features,
):
    if not isinstance(
        df,
        pd.DataFrame,
    ):
        raise TypeError(
            "최종 학습 데이터는 "
            "DataFrame이어야 합니다."
        )

    if df.empty:
        raise ValueError(
            "최종 학습 데이터가 "
            "비어 있습니다."
        )

    required_columns = {
        "Date",
        "Ticker",
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
            "최종 학습 데이터에 필요한 "
            "컬럼이 없습니다: "
            + ", ".join(
                sorted(
                    missing_columns
                )
            )
        )

    return True


def prepare_final_training_dataset(
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


def get_candidate_model_params(
    candidate_model_data,
):
    model_params = (
        candidate_model_data.get(
            "model_params"
        )
    )

    if model_params is not None:
        if not isinstance(
            model_params,
            dict,
        ):
            raise TypeError(
                "후보 모델 파라미터는 "
                "dict 형식이어야 합니다."
            )

        return dict(
            model_params
        )

    candidate_model = (
        candidate_model_data.get(
            "model"
        )
    )

    if candidate_model is None:
        raise ValueError(
            "후보 모델 파라미터를 "
            "확인할 수 없습니다."
        )

    return dict(
        candidate_model.get_params()
    )


def train_final_candidate_model(
    candidate_path,
    output_path=None,
    dataset_path=DATASET_PATH,
):
    candidate_path = Path(
        candidate_path
    )

    if output_path is None:
        output_path = (
            candidate_path
        )

    output_path = Path(
        output_path
    )

    dataset_path = Path(
        dataset_path
    )

    candidate_model_data = (
        load_model_data(
            candidate_path
        )
    )

    features = list(
        candidate_model_data[
            "features"
        ]
    )

    model_params = (
        get_candidate_model_params(
            candidate_model_data
        )
    )

    df = pd.read_csv(
        dataset_path
    )

    validate_final_training_dataset(
        df=df,
        features=features,
    )

    df = prepare_final_training_dataset(
        df
    )

    X_train = (
        df[
            features
        ]
        .fillna(0)
    )

    y_train = df[
        "Target"
    ]

    if X_train.empty:
        raise ValueError(
            "최종 모델 학습 데이터가 "
            "없습니다."
        )

    if (
        y_train.nunique()
        < 2
    ):
        raise ValueError(
            "최종 모델 학습 Target 클래스가 "
            "2개 미만입니다."
        )

    model = create_model(
        model_params=model_params
    )

    model.fit(
        X_train,
        y_train,
    )

    trained_at = (
        datetime.now().isoformat(
            timespec="seconds"
        )
    )

    final_model_data = {
        **candidate_model_data,

        "model": model,

        "model_params": (
            model.get_params()
        ),

        "trained_at": (
            trained_at
        ),

        "train_start_date": str(
            df[
                "Date"
            ]
            .min()
            .date()
        ),

        "train_end_date": str(
            df[
                "Date"
            ]
            .max()
            .date()
        ),

        "validation_start_date": None,

        "validation_end_date": None,

        "model_role": (
            "candidate"
        ),

        "training_mode": (
            "full_dataset_after_validation"
        ),

        "training_row_count": int(
            len(
                X_train
            )
        ),

        "training_date_count": int(
            df[
                "Date"
            ].nunique()
        ),

        "source_candidate_path": str(
            candidate_path
        ),

        "model_path": str(
            output_path
        ),
    }

    save_model_data_atomic(
        model_data=final_model_data,
        model_path=output_path,
    )

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "최종 후보 모델 전체 데이터 재학습 완료"
    )

    print(
        "#"
        * 80
    )

    print(
        f"원본 후보 모델: "
        f"{candidate_path}"
    )

    print(
        f"최종 모델 저장: "
        f"{output_path}"
    )

    print(
        f"Feature Subset: "
        f"{final_model_data['subset_name']}"
    )

    print(
        f"Feature 수: "
        f"{len(features)}"
    )

    print(
        f"전체 학습 행 수: "
        f"{len(X_train):,}"
    )

    print(
        f"고유 학습 날짜 수: "
        f"{final_model_data['training_date_count']:,}"
    )

    print(
        "전체 학습 기간: "
        f"{final_model_data['train_start_date']} "
        f"~ "
        f"{final_model_data['train_end_date']}"
    )

    print(
        f"학습 방식: "
        f"{final_model_data['training_mode']}"
    )

    return final_model_data


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "평가를 마친 후보 모델 설정으로 "
            "전체 데이터 최종 재학습"
        )
    )

    parser.add_argument(
        "--candidate-path",
        required=True,
        type=str,
        help=(
            "재학습할 후보 모델 경로"
        ),
    )

    parser.add_argument(
        "--output-path",
        default=None,
        type=str,
        help=(
            "최종 모델 저장 경로. "
            "생략하면 원본 후보 파일을 "
            "덮어씁니다."
        ),
    )

    parser.add_argument(
        "--dataset-path",
        default=str(
            DATASET_PATH
        ),
        type=str,
        help=(
            "학습 데이터셋 경로"
        ),
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    train_final_candidate_model(
        candidate_path=(
            args.candidate_path
        ),
        output_path=(
            args.output_path
        ),
        dataset_path=(
            args.dataset_path
        ),
    )
