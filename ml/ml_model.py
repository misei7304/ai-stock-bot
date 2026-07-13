from sklearn.ensemble import (
    RandomForestClassifier,
)


def create_model():
    return RandomForestClassifier(
        n_estimators=500,
        max_depth=7,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )