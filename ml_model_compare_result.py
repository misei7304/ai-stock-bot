import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


DATASET_PATH = "ml/training_dataset.csv"
RESULT_PATH = "ml/model_compare_result.csv"


def compare_models_and_save():
    df = pd.read_csv(DATASET_PATH)

    X = df.drop(columns=[
        "Target",
        "Future_Return_5D"
    ])
    y = df["Target"]

    X = X.select_dtypes(include=["number"]).fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    models = {
        "LogisticRegression": LogisticRegression(max_iter=3000),
        "RandomForest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced"
        ),
        "XGBoost": XGBClassifier(
            n_estimators=400,
            max_depth=3,
            learning_rate=0.03,
            subsample=0.9,
            colsample_bytree=0.9,
            scale_pos_weight=1.5,
            eval_metric="logloss",
            random_state=42
        )
    }

    results = []

    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        results.append({
            "model": name,
            "accuracy": accuracy_score(y_test, pred),
            "precision_1": precision_score(y_test, pred, zero_division=0),
            "recall_1": recall_score(y_test, pred, zero_division=0),
            "f1_1": f1_score(y_test, pred, zero_division=0),
        })

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by="f1_1", ascending=False)

    print("\n" + "#" * 80)
    print("ML 모델 비교 결과 저장")
    print("#" * 80)
    print(result_df.to_string(index=False))

    result_df.to_csv(RESULT_PATH, index=False)
    print(f"\n저장 완료: {RESULT_PATH}")


if __name__ == "__main__":
    compare_models_and_save()