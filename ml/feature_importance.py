import pandas as pd

from ml.ml_features import ALL_FEATURES
from ml.ml_model import create_model


DATASET_PATH = "ml/training_dataset.csv"
RESULT_PATH = "ml/feature_importance.csv"


def calculate_feature_importance():
    df = pd.read_csv(
        DATASET_PATH
    )

    missing_features = [
        feature
        for feature in ALL_FEATURES
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            "학습 데이터셋에 필요한 Feature가 없습니다: "
            + ", ".join(
                missing_features
            )
        )

    if "Target" not in df.columns:
        raise ValueError(
            "학습 데이터셋에 Target 컬럼이 없습니다."
        )

    X = (
        df[
            ALL_FEATURES
        ]
        .fillna(0)
    )

    y = df["Target"]

    model = create_model()

    model.fit(
        X,
        y,
    )

    importance_df = pd.DataFrame({
        "Feature": ALL_FEATURES,
        "Importance": (
            model.feature_importances_
        ),
    })

    total_importance = (
        importance_df[
            "Importance"
        ].sum()
    )

    if total_importance > 0:
        importance_df[
            "Percent"
        ] = (
            importance_df[
                "Importance"
            ]
            / total_importance
            * 100
        )
    else:
        importance_df[
            "Percent"
        ] = 0.0

    importance_df = (
        importance_df
        .sort_values(
            by="Importance",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )

    importance_df[
        "Rank"
    ] = (
        importance_df.index
        + 1
    )

    importance_df = importance_df[
        [
            "Rank",
            "Feature",
            "Importance",
            "Percent",
        ]
    ]

    importance_df.to_csv(
        RESULT_PATH,
        index=False,
    )

    print("\n" + "#" * 80)
    print("Feature Importance")
    print("#" * 80)

    for _, row in importance_df.iterrows():
        print(
            f"{int(row['Rank'])}위 | "
            f"{row['Feature']} | "
            f"Importance "
            f"{row['Importance']:.6f} | "
            f"비중 "
            f"{row['Percent']:.2f}%"
        )

    print(
        "\nCSV 저장 완료: "
        f"{RESULT_PATH}"
    )

    return importance_df


if __name__ == "__main__":
    calculate_feature_importance()