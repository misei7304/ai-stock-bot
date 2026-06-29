from sklearn.ensemble import RandomForestClassifier


def create_model():
    return RandomForestClassifier(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42
    )