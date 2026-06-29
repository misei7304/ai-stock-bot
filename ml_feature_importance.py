import pandas as pd

from sklearn.ensemble import RandomForestClassifier

DATASET_PATH = "ml/training_dataset.csv"


def feature_importance():

    df = pd.read_csv(DATASET_PATH)

    X = df.drop(columns=[
        "Target",
        "Future_Return_5D"
    ])

    y = df["Target"]

    X = X.select_dtypes(include=["number"]).fillna(0)

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X, y)

    importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.feature_importances_
    })

    importance = importance.sort_values(
        by="Importance",
        ascending=False
    )

    print("\n" + "#" * 80)
    print("Feature Importance")
    print("#" * 80)

    print(importance.to_string(index=False))


if __name__ == "__main__":
    feature_importance()