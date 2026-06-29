import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from ml.ml_features import FEATURES


DATASET_PATH = "ml/training_dataset.csv"
RESULT_PATH = "ml/hyperparameter_tuning_result.csv"

PARAM_SETS = [
    {"n_estimators": 200, "max_depth": 5, "min_samples_leaf": 5},
    {"n_estimators": 300, "max_depth": 5, "min_samples_leaf": 5},
    {"n_estimators": 300, "max_depth": 7, "min_samples_leaf": 5},
    {"n_estimators": 300, "max_depth": 10, "min_samples_leaf": 5},
    {"n_estimators": 500, "max_depth": 7, "min_samples_leaf": 5},
    {"n_estimators": 500, "max_depth": 10, "min_samples_leaf": 5},
    {"n_estimators": 500, "max_depth": 10, "min_samples_leaf": 10},
]


def run_tuning():
    df = pd.read_csv(DATASET_PATH)

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date")

    unique_dates = sorted(df["Date"].unique())

    train_window = int(len(unique_dates) * 0.6)
    test_window = int(len(unique_dates) * 0.1)
    step_size = test_window

    threshold = 0.70

    results = []

    print("\n" + "#" * 80)
    print("Hyperparameter Tuning Walk-Forward 검증")
    print("#" * 80)

    for params in PARAM_SETS:
        print("\n" + "=" * 80)
        print(f"Params: {params}")
        print("=" * 80)

        fold_rows = []
        fold = 1

        for start in range(0, len(unique_dates) - train_window - test_window, step_size):
            train_start = unique_dates[start]
            train_end = unique_dates[start + train_window - 1]

            test_start = unique_dates[start + train_window]
            test_end = unique_dates[start + train_window + test_window - 1]

            train_df = df[
                (df["Date"] >= train_start) &
                (df["Date"] <= train_end)
            ].copy()

            test_df = df[
                (df["Date"] >= test_start) &
                (df["Date"] <= test_end)
            ].copy()

            X_train = train_df[FEATURES].fillna(0)
            y_train = train_df["Target"]

            X_test = test_df[FEATURES].fillna(0)
            y_test = test_df["Target"]

            model = RandomForestClassifier(
                n_estimators=params["n_estimators"],
                max_depth=params["max_depth"],
                min_samples_leaf=params["min_samples_leaf"],
                random_state=42,
                class_weight="balanced",
                n_jobs=-1,
            )

            model.fit(X_train, y_train)

            pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, pred)

            test_df["Probability"] = model.predict_proba(X_test)[:, 1]
            signal_df = test_df[test_df["Probability"] >= threshold].copy()

            if signal_df.empty:
                trade_count = 0
                win_rate = None
                avg_return = None
                median_return = None
                print(f"Fold {fold} | 신호 없음 | 정확도 {accuracy:.2%}")
            else:
                trade_count = len(signal_df)
                win_rate = (signal_df["Future_Return_5D"] >= 0.03).mean()
                avg_return = signal_df["Future_Return_5D"].mean()
                median_return = signal_df["Future_Return_5D"].median()

                print(
                    f"Fold {fold} | "
                    f"신호 {trade_count}개 | "
                    f"성공률 {win_rate:.2%} | "
                    f"평균수익 {avg_return:.2%} | "
                    f"정확도 {accuracy:.2%}"
                )

            fold_rows.append({
                "params": str(params),
                "fold": fold,
                "accuracy": accuracy,
                "trade_count": trade_count,
                "win_rate": win_rate,
                "avg_return_5d": avg_return,
                "median_return_5d": median_return,
            })

            fold += 1

        fold_df = pd.DataFrame(fold_rows)
        valid_signal = fold_df[fold_df["trade_count"] > 0]

        if valid_signal.empty:
            total_trades = 0
            avg_win_rate = None
            avg_return = None
            median_return = None
        else:
            total_trades = valid_signal["trade_count"].sum()
            avg_win_rate = valid_signal["win_rate"].mean()
            avg_return = valid_signal["avg_return_5d"].mean()
            median_return = valid_signal["median_return_5d"].mean()

        results.append({
            "params": str(params),
            "avg_accuracy": fold_df["accuracy"].mean(),
            "total_trades": total_trades,
            "avg_win_rate": avg_win_rate,
            "avg_return_5d": avg_return,
            "median_return_5d": median_return,
        })

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(
        by=["avg_return_5d", "avg_win_rate"],
        ascending=False
    )

    print("\n" + "#" * 80)
    print("Hyperparameter Tuning 최종 결과")
    print("#" * 80)
    print(result_df.to_string(index=False))

    result_df.to_csv(RESULT_PATH, index=False)
    print(f"\nCSV 저장 완료: {RESULT_PATH}")


if __name__ == "__main__":
    run_tuning()