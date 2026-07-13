from sklearn.ensemble import (
    RandomForestClassifier,
)


DEFAULT_MODEL_PARAMS = {
    "n_estimators": 500,
    "max_depth": 7,
    "min_samples_leaf": 5,
    "class_weight": "balanced",
    "random_state": 42,
    "n_jobs": -1,
}


def validate_model_params(
    model_params,
):
    if model_params is None:
        return True

    if not isinstance(
        model_params,
        dict,
    ):
        raise TypeError(
            "모델 파라미터는 "
            "dict 형식이어야 합니다."
        )

    valid_parameter_names = set(
        RandomForestClassifier()
        .get_params()
        .keys()
    )

    invalid_parameter_names = (
        set(
            model_params.keys()
        )
        - valid_parameter_names
    )

    if invalid_parameter_names:
        raise ValueError(
            "지원하지 않는 RandomForest "
            "파라미터가 있습니다: "
            + ", ".join(
                sorted(
                    invalid_parameter_names
                )
            )
        )

    return True


def create_model(
    model_params=None,
):
    validate_model_params(
        model_params
    )

    final_model_params = dict(
        DEFAULT_MODEL_PARAMS
    )

    if model_params is not None:
        final_model_params.update(
            model_params
        )

    return RandomForestClassifier(
        **final_model_params
    )
