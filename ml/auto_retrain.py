import argparse
import json
import os
import traceback

from datetime import (
    datetime,
)
from pathlib import (
    Path,
)

from ml.build_dataset import (
    build_training_dataset,
)
from ml.model_evaluator import (
    evaluate_candidate_model,
)
from ml.model_repository import (
    EVALUATION_DIR,
    create_candidate_model_path,
    initialize_model_store,
)
from ml.train_model import (
    train_model,
)


AUTO_RETRAIN_RESULT_DIR = (
    EVALUATION_DIR
    / "auto_retrain"
)


def initialize_auto_retrain_store():
    initialize_model_store()

    AUTO_RETRAIN_RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


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

    if hasattr(
        value,
        "item",
    ):
        try:
            return value.item()
        except (
            TypeError,
            ValueError,
        ):
            pass

    return value


def save_auto_retrain_result(
    result,
):
    initialize_auto_retrain_store()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    result_path = (
        AUTO_RETRAIN_RESULT_DIR
        / (
            "auto_retrain_"
            f"{timestamp}.json"
        )
    )

    temporary_path = (
        result_path.with_suffix(
            ".json.tmp"
        )
    )

    serializable_result = (
        make_json_serializable(
            result
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
        result_path,
    )

    return result_path


def run_auto_retrain(
    rebuild_dataset=True,
    promote=True,
):
    initialize_auto_retrain_store()

    started_at = datetime.now()

    result = {
        "started_at": (
            started_at.isoformat(
                timespec="seconds"
            )
        ),
        "finished_at": None,
        "status": "running",
        "rebuild_dataset_requested": bool(
            rebuild_dataset
        ),
        "promotion_requested": bool(
            promote
        ),
        "dataset_rebuilt": False,
        "candidate_created": False,
        "candidate_model_path": None,
        "evaluation_completed": False,
        "promotion_approved": False,
        "promotion_executed": False,
        "evaluation_result": None,
        "error_type": None,
        "error_message": None,
        "traceback": None,
    }

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "ML 자동 재학습 시작"
    )

    print(
        "#"
        * 80
    )

    try:
        if rebuild_dataset:
            print(
                "\n1. 학습 데이터셋 재생성"
            )

            build_result = (
                build_training_dataset()
            )

            result[
                "dataset_rebuilt"
            ] = True

            result[
                "dataset_build_result"
            ] = (
                build_result
            )

        else:
            print(
                "\n1. 학습 데이터셋 재생성 생략"
            )

        print(
            "\n2. 후보 모델 학습"
        )

        candidate_path = (
            create_candidate_model_path()
        )

        candidate_model_data = train_model(
            output_path=candidate_path,
            model_role="candidate",
        )

        result[
            "candidate_created"
        ] = True

        result[
            "candidate_model_path"
        ] = str(
            candidate_path
        )

        result[
            "candidate_trained_at"
        ] = candidate_model_data.get(
            "trained_at"
        )

        result[
            "candidate_subset_name"
        ] = candidate_model_data.get(
            "subset_name"
        )

        result[
            "candidate_model_params"
        ] = candidate_model_data.get(
            "model_params"
        )

        print(
            "\n3. 운영 모델과 후보 모델 비교"
        )

        evaluation_result = (
            evaluate_candidate_model(
                candidate_path=(
                    candidate_path
                ),
                promote=promote,
            )
        )

        promotion_decision = (
            evaluation_result[
                "promotion_decision"
            ]
        )

        result[
            "evaluation_completed"
        ] = True

        result[
            "promotion_approved"
        ] = bool(
            promotion_decision[
                "approved"
            ]
        )

        result[
            "promotion_executed"
        ] = bool(
            evaluation_result[
                "promotion_executed"
            ]
        )

        result[
            "evaluation_result"
        ] = evaluation_result

        result[
            "status"
        ] = "completed"

        print(
            "\n"
            + "="
            * 80
        )

        print(
            "자동 재학습 결과"
        )

        print(
            "="
            * 80
        )

        print(
            "후보 모델 생성: "
            f"{result['candidate_created']}"
        )

        print(
            "승격 승인: "
            f"{result['promotion_approved']}"
        )

        print(
            "실제 승격 실행: "
            f"{result['promotion_executed']}"
        )

        if (
            result[
                "promotion_executed"
            ]
        ):
            print(
                "결과: 후보 모델이 "
                "운영 모델로 승격되었습니다."
            )

        else:
            print(
                "결과: 기존 운영 모델을 "
                "유지합니다."
            )

    except Exception as error:
        result[
            "status"
        ] = "failed"

        result[
            "error_type"
        ] = (
            error.__class__.__name__
        )

        result[
            "error_message"
        ] = str(
            error
        )

        result[
            "traceback"
        ] = traceback.format_exc()

        print(
            "\n자동 재학습 실패"
        )

        print(
            f"오류 종류: "
            f"{result['error_type']}"
        )

        print(
            f"오류 내용: "
            f"{result['error_message']}"
        )

        print(
            "운영 모델은 변경하지 않습니다."
        )

    finally:
        finished_at = datetime.now()

        result[
            "finished_at"
        ] = finished_at.isoformat(
            timespec="seconds"
        )

        result[
            "duration_seconds"
        ] = (
            finished_at
            - started_at
        ).total_seconds()

        result_path = (
            save_auto_retrain_result(
                result
            )
        )

        print(
            "\n자동 재학습 결과 저장 완료: "
            f"{result_path}"
        )

    if (
        result[
            "status"
        ]
        == "failed"
    ):
        raise RuntimeError(
            "자동 재학습이 실패했습니다: "
            f"{result['error_message']}"
        )

    return result


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "학습 데이터셋 생성, "
            "후보 모델 학습, 평가, "
            "승격을 자동 실행합니다."
        )
    )

    parser.add_argument(
        "--skip-dataset",
        action="store_true",
        help=(
            "학습 데이터셋 재생성을 "
            "생략합니다."
        ),
    )

    parser.add_argument(
        "--no-promote",
        action="store_true",
        help=(
            "후보 모델을 평가만 하고 "
            "승격하지 않습니다."
        ),
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    run_auto_retrain(
        rebuild_dataset=(
            not args.skip_dataset
        ),
        promote=(
            not args.no_promote
        ),
    )