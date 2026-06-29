import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


DATASET_PATH = "ml/training_dataset.csv"


def compare_models():
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

    print("\n" + "#" * 80)
    print("ML 모델 성능 비교")
    print("#" * 80)

    for name, model in models.items():
        model.fit(X_train, y_train)

        pred = model.predict(X_test)
        acc = accuracy_score(y_test, pred)

        print(f"\n[{name}]")
        print(f"정확도: {acc * 100:.2f}%")
        print(classification_report(y_test, pred))


if __name__ == "__main__":
    compare_models()