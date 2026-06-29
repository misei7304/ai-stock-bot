import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from ml.ml_features import FEATURES
from ml.ml_model import create_model


df = pd.read_csv("ml/training_dataset.csv")

X = df[FEATURES]
y = df["Target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

model = create_model()
model.fit(X_train, y_train)

pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)

print("\n=== 통합 모델 학습 결과 ===")
print(f"정확도: {accuracy:.2%}")
print("\n=== 상세 결과 ===")
print(classification_report(y_test, pred, zero_division=0))

joblib.dump(model, "ml/trained_model.pkl")

print("\n모델 저장 완료: ml/trained_model.pkl")