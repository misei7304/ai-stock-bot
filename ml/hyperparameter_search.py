import argparse
import itertools
import json
import random

from pathlib import (
    Path,
)

from ml.ml_model import (
    create_model,
)
from ml.model_repository import (
    ACTIVE_MODEL_PATH,
    load_model_data,
)


DEFAULT_CANDIDATE_COUNT = 12

DEFAULT_RANDOM_SEED = 42


HYPERPARAMETER_SEARCH_SPACE = {
    "n_estimators": [
        300,
        500,
        700,
    ],
    "max_depth": [
        5,
        7,
        10,
        15,
        None,
    ],
    "min_samples_leaf": [
        3,
        5,
        10,
        20,
    ],
    "min_samples_split": [
        2,
        5,
        10,
    ],
    "max_features": [
        "sqrt",
        "log2",
        0.5,
    ],
    "class_weight": [
        "balanced",
        "balanced_subsample",
    ],
}


SEARCH_PARAMETER_NAMES = tuple(
    HYPERPARAMETER_SEARCH_SPACE.keys()
)


def validate_candidate_count(
    candidate_count,
):
    if not isinstance(
        candidate_count,
        int,
    ):
        raise TypeError(
            "파라미터 후보 수는 "
            "정수여야 합니다."
        )

    if candidate_count <= 0:
        raise ValueError(
            "파라미터 후보 수는 "
            "1 이상이어야 합니다."
        )

    return True


def validate_random_seed(
    random_seed,
):
    if not isinstance(
        random_seed,
        int,
    ):
        raise TypeError(
            "Random Seed는 "
            "정수여야 합니다."
        )

    return True


def get_base_model_params(
    model_data,
):
    model_params = (
        model_data.get(
            "model_params"
        )
    )

    if model_params is None:
        model = model_data.get(
            "model"
        )

        if model is None:
            raise ValueError(
                "기준 모델 파라미터를 "
                "확인할 수 없습니다."
            )

        model_params = (
            model.get_params()
        )

    if not isinstance(
        model_params,
        dict,
    ):
        raise TypeError(
            "기준 모델 파라미터는 "
            "dict 형식이어야 합니다."
        )

    return dict(
        model_params
    )


def get_search_param_subset(
    model_params,
):
    return {
        parameter_name: (
            model_params[
                parameter_name
            ]
        )
        for parameter_name
        in SEARCH_PARAMETER_NAMES
    }


def create_parameter_signature(
    model_params,
):
    search_params = (
        get_search_param_subset(
            model_params
        )
    )

    return tuple(
        (
            parameter_name,
            search_params[
                parameter_name
            ],
        )
        for parameter_name
        in SEARCH_PARAMETER_NAMES
    )


def generate_all_search_combinations():
    parameter_value_lists = [
        HYPERPARAMETER_SEARCH_SPACE[
            parameter_name
        ]
        for parameter_name
        in SEARCH_PARAMETER_NAMES
    ]

    combinations = []

    for values in itertools.product(
        *parameter_value_lists
    ):
        combination = {
            parameter_name: value
            for (
                parameter_name,
                value,
            )
            in zip(
                SEARCH_PARAMETER_NAMES,
                values,
            )
        }

        combinations.append(
            combination
        )

    return combinations


def merge_model_params(
    base_model_params,
    search_params,
):
    merged_params = dict(
        base_model_params
    )

    merged_params.update(
        search_params
    )

    return merged_params


def validate_generated_model_params(
    model_params,
):
    model = create_model(
        model_params=model_params
    )

    recreated_params = (
        model.get_params()
    )

    for (
        parameter_name,
        expected_value,
    ) in model_params.items():
        actual_value = (
            recreated_params[
                parameter_name
            ]
        )

        if (
            actual_value
            != expected_value
        ):
            raise ValueError(
                "생성된 모델 파라미터가 "
                "요청값과 다릅니다. "
                f"{parameter_name}: "
                f"요청={expected_value}, "
                f"생성={actual_value}"
            )

    return True


def generate_hyperparameter_candidates(
    base_model_params,
    candidate_count=(
        DEFAULT_CANDIDATE_COUNT
    ),
    random_seed=(
        DEFAULT_RANDOM_SEED
    ),
):
    validate_candidate_count(
        candidate_count
    )

    validate_random_seed(
        random_seed
    )

    if not isinstance(
        base_model_params,
        dict,
    ):
        raise TypeError(
            "기준 모델 파라미터는 "
            "dict 형식이어야 합니다."
        )

    validate_generated_model_params(
        base_model_params
    )

    all_combinations = (
        generate_all_search_combinations()
    )

    base_signature = (
        create_parameter_signature(
            base_model_params
        )
    )

    available_combinations = []

    for search_params in (
        all_combinations
    ):
        merged_params = (
            merge_model_params(
                base_model_params=(
                    base_model_params
                ),
                search_params=(
                    search_params
                ),
            )
        )

        signature = (
            create_parameter_signature(
                merged_params
            )
        )

        if signature == base_signature:
            continue

        available_combinations.append(
            search_params
        )

    maximum_candidate_count = (
        1
        + len(
            available_combinations
        )
    )

    if (
        candidate_count
        > maximum_candidate_count
    ):
        raise ValueError(
            "요청한 후보 수가 전체 가능한 "
            "파라미터 조합보다 많습니다. "
            f"요청={candidate_count}, "
            f"가능={maximum_candidate_count}"
        )

    random_generator = random.Random(
        random_seed
    )

    sample_count = (
        candidate_count
        - 1
    )

    sampled_combinations = (
        random_generator.sample(
            available_combinations,
            sample_count,
        )
        if sample_count > 0
        else []
    )

    candidates = []

    base_candidate = {
        "candidate_number": 1,
        "candidate_type": (
            "champion_baseline"
        ),
        "model_params": dict(
            base_model_params
        ),
        "search_params": (
            get_search_param_subset(
                base_model_params
            )
        ),
    }

    candidates.append(
        base_candidate
    )

    for (
        index,
        search_params,
    ) in enumerate(
        sampled_combinations,
        start=2,
    ):
        model_params = (
            merge_model_params(
                base_model_params=(
                    base_model_params
                ),
                search_params=(
                    search_params
                ),
            )
        )

        validate_generated_model_params(
            model_params
        )

        candidate = {
            "candidate_number": int(
                index
            ),
            "candidate_type": (
                "random_search"
            ),
            "model_params": (
                model_params
            ),
            "search_params": dict(
                search_params
            ),
        }

        candidates.append(
            candidate
        )

    signatures = [
        create_parameter_signature(
            candidate[
                "model_params"
            ]
        )
        for candidate
        in candidates
    ]

    if (
        len(
            signatures
        )
        != len(
            set(
                signatures
            )
        )
    ):
        raise ValueError(
            "중복된 Hyperparameter 후보가 "
            "생성되었습니다."
        )

    return candidates


def print_hyperparameter_candidates(
    candidates,
):
    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "Hyperparameter 후보 생성 결과"
    )

    print(
        "#"
        * 80
    )

    print(
        f"후보 수: "
        f"{len(candidates)}"
    )

    for candidate in candidates:
        print(
            "\n"
            f"[Candidate "
            f"{candidate['candidate_number']}]"
        )

        print(
            f"유형: "
            f"{candidate['candidate_type']}"
        )

        for (
            parameter_name,
            parameter_value,
        ) in (
            candidate[
                "search_params"
            ].items()
        ):
            print(
                f"{parameter_name}: "
                f"{parameter_value}"
            )


def save_hyperparameter_candidates(
    candidates,
    output_path,
):
    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = (
        output_path.with_suffix(
            output_path.suffix
            + ".tmp"
        )
    )

    with temporary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            candidates,
            file,
            ensure_ascii=False,
            indent=2,
        )

    temporary_path.replace(
        output_path
    )

    return output_path


def generate_saved_model_candidates(
    model_path=ACTIVE_MODEL_PATH,
    candidate_count=(
        DEFAULT_CANDIDATE_COUNT
    ),
    random_seed=(
        DEFAULT_RANDOM_SEED
    ),
):
    model_data = load_model_data(
        model_path
    )

    base_model_params = (
        get_base_model_params(
            model_data
        )
    )

    return generate_hyperparameter_candidates(
        base_model_params=(
            base_model_params
        ),
        candidate_count=(
            candidate_count
        ),
        random_seed=(
            random_seed
        ),
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "RandomForest Hyperparameter "
            "후보 생성"
        )
    )

    parser.add_argument(
        "--model-path",
        type=str,
        default=str(
            ACTIVE_MODEL_PATH
        ),
        help=(
            "기준 모델 경로"
        ),
    )

    parser.add_argument(
        "--candidate-count",
        type=int,
        default=(
            DEFAULT_CANDIDATE_COUNT
        ),
        help=(
            "Champion 기준 설정을 포함한 "
            "전체 후보 수"
        ),
    )

    parser.add_argument(
        "--random-seed",
        type=int,
        default=(
            DEFAULT_RANDOM_SEED
        ),
        help=(
            "후보 샘플링 Random Seed"
        ),
    )

    parser.add_argument(
        "--output-path",
        type=str,
        default=None,
        help=(
            "후보 목록 JSON 저장 경로"
        ),
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    generated_candidates = (
        generate_saved_model_candidates(
            model_path=(
                args.model_path
            ),
            candidate_count=(
                args.candidate_count
            ),
            random_seed=(
                args.random_seed
            ),
        )
    )

    print_hyperparameter_candidates(
        generated_candidates
    )

    if (
        args.output_path
        is not None
    ):
        saved_path = (
            save_hyperparameter_candidates(
                candidates=(
                    generated_candidates
                ),
                output_path=(
                    args.output_path
                ),
            )
        )

        print(
            "\n후보 JSON 저장 완료: "
            f"{saved_path}"
        )
