import pandas as pd

from ml.ml_features import FEATURES
from ml.ml_model import create_model


DATASET_PATH = "ml/training_dataset.csv"


FEATURE_SETS = {
    "current_10_features": FEATURES,
    "top_8_features": [
        "ATR_Percent",
        "MA60_Ratio",
        "MACD_Signal",
        "MACD",
        "ATR",
        "RSI",
        "High_Low_Range",
        "MA60",
    ],
    "top_6_features": [
        "ATR_Percent",
        "MA60_Ratio",
        "MACD_Signal",
        "MACD",
        "ATR",
        "RSI",
    ],
}


def run_feature_pruning_backtest():
    df = pd.read_csv(DATASET_PATH)

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date")

    unique_dates = sorted(df["Date"].unique())

    train_window = int(len(unique_dates) * 0.6)
    test_window = int(len(unique_dates) * 0.1)
    step_size = test_window

    threshold = 0.70

    print("\n" + "#" * 80)
    print("Feature Pruning Walk-Forward 검증")
    print("#" * 80)

    results = []

    for feature_set_name, feature_list in FEATURE_SETS.items():
        print("\n" + "=" * 80)
        print(f"Feature Set: {feature_set_name}")
        print(f"Feature Count: {len(feature_list)}")
        print("=" * 80)

        fold_results = []
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

            X_train = train_df[feature_list].fillna(0)
            y_train = train_df["Target"]

            X_test = test_df[feature_list].fillna(0)

            model = create_model()
            model.fit(X_train, y_train)

            test_df["Probability"] = model.predict_proba(X_test)[:, 1]

            signal_df = test_df[test_df["Probability"] >= threshold].copy()

            if signal_df.empty:
                trade_count = 0
                win_rate = None
                avg_return = None
                median_return = None
            else:
                trade_count = len(signal_df)
                win_rate = (signal_df["Future_Return_5D"] >= 0.03).mean()
                avg_return = signal_df["Future_Return_5D"].mean()
                median_return = signal_df["Future_Return_5D"].median()

            print(
                f"Fold {fold} | "
                f"신호 {trade_count}개 | "
                f"성공률 {win_rate:.2%} | "
                f"평균수익 {avg_return:.2%}"
                if trade_count > 0
                else f"Fold {fold} | 신호 없음"
            )

            fold_results.append({
                "feature_set": feature_set_name,
                "fold": fold,
                "feature_count": len(feature_list),
                "trade_count": trade_count,
                "win_rate": win_rate,
                "avg_return_5d": avg_return,
                "median_return_5d": median_return,
            })

            fold += 1

        valid = pd.DataFrame(fold_results)
        valid_signal = valid[valid["trade_count"] > 0]

        if valid_signal.empty:
            print("전체 신호 없음")
            continue

        total_trades = valid_signal["trade_count"].sum()
        avg_win_rate = valid_signal["win_rate"].mean()
        avg_return = valid_signal["avg_return_5d"].mean()
        median_return = valid_signal["median_return_5d"].mean()

        results.append({
            "feature_set": feature_set_name,
            "feature_count": len(feature_list),
            "total_trades": total_trades,
            "avg_win_rate": avg_win_rate,
            "avg_return_5d": avg_return,
            "median_return_5d": median_return,
        })

        print("\n요약")
        print(f"총 신호 수: {total_trades}")
        print(f"평균 성공률: {avg_win_rate:.2%}")
        print(f"평균 5일 수익률: {avg_return:.2%}")
        print(f"중앙값 평균 5일 수익률: {median_return:.2%}")

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by="avg_return_5d", ascending=False)

    print("\n" + "#" * 80)
    print("Feature Pruning 최종 비교")
    print("#" * 80)
    print(result_df.to_string(index=False))

    result_df.to_csv("ml/feature_pruning_result.csv", index=False)
    print("\nCSV 저장 완료: ml/feature_pruning_result.csv")


if __name__ == "__main__":
    run_feature_pruning_backtest()