import pandas as pd

from ml.ml_features import (
    ALL_FEATURES,
    BASE_FEATURES,
    NEW_FEATURES,
)
from ml.ml_model import create_model


DATASET_PATH = "ml/training_dataset.csv"


FEATURE_SETS = {
    "base_10_features": (
        BASE_FEATURES
    ),
    "new_6_only": (
        NEW_FEATURES
    ),
    "combined_16_features": (
        ALL_FEATURES
    ),
    "base_plus_trend": (
        BASE_FEATURES
        + [
            "MA120_Ratio",
            "Distance_From_20D_High",
            "Volatility_20",
        ]
    ),
    "base_plus_volume": (
        BASE_FEATURES
        + [
            "Volume_Ratio_20",
            "Turnover_Ratio_20",
            "OBV_Imbalance_20",
        ]
    ),
}


def run_feature_pruning_backtest():
    df = pd.read_csv(DATASET_PATH)

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date")

    unique_dates = sorted(df["Date"].unique())

    train_window = int(len(unique_dates) * 0.6)
    test_window = int(len(unique_dates) * 0.1)
    step_size = test_window

    thresholds = [
        0.70,
        0.75,
        0.80,
    ]

    print("\n" + "#" * 80)
    print("Feature Pruning Walk-Forward 검증")
    print("#" * 80)

    results = []

    for feature_set_name, feature_list in FEATURE_SETS.items():
        for threshold in thresholds:
            print("\n" + "=" * 80)
            print(f"Feature Set: {feature_set_name}")
            print(f"Feature Count: {len(feature_list)}")
            print("=" * 80)

            fold_results = []
            all_signal_results = []
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

                signal_result = signal_df[
                    [
                        "Ticker",
                        "Date",
                        "Future_Return_5D",
                    ]
                ].copy()

                signal_result[
                    "feature_set"
                ] = feature_set_name

                signal_result[
                    "fold"
                ] = fold

                all_signal_results.append(
                    signal_result
                )

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

            total_trades = int(
                valid_signal[
                    "trade_count"
                ].sum()
            )

            combined_signals = pd.concat(
                all_signal_results,
                ignore_index=True,
            )

            weighted_win_rate = (
                combined_signals[
                    "Future_Return_5D"
                ] >= 0.03
            ).mean()

            weighted_avg_return = (
                combined_signals[
                    "Future_Return_5D"
                ].mean()
            )

            weighted_median_return = (
                combined_signals[
                    "Future_Return_5D"
                ].median()
            )

            profitable_rate = (
                combined_signals[
                    "Future_Return_5D"
                ] > 0
            ).mean()

            return_std = (
                combined_signals[
                    "Future_Return_5D"
                ].std()
            )

            worst_return = (
                combined_signals[
                    "Future_Return_5D"
                ].min()
            )

            best_return = (
                combined_signals[
                    "Future_Return_5D"
                ].max()
            )

            results.append({
                "feature_set": feature_set_name,
                "threshold": threshold,
                "feature_count": len(feature_list),
                "total_trades": total_trades,
                "success_rate_3pct": weighted_win_rate,
                "profitable_rate": profitable_rate,
                "avg_return_5d": weighted_avg_return,
                "median_return_5d": weighted_median_return,
                "return_std": return_std,
                "worst_return": worst_return,
                "best_return": best_return,
            })

            print("\n요약")
            print(
                f"총 신호 수: "
                f"{total_trades}"
            )
            print(
                "전체 +3% 성공률: "
                f"{weighted_win_rate:.2%}"
            )
            print(
                "전체 수익 발생률: "
                f"{profitable_rate:.2%}"
            )
            print(
                "전체 평균 5일 수익률: "
                f"{weighted_avg_return:.2%}"
            )
            print(
                "전체 중앙값 5일 수익률: "
                f"{weighted_median_return:.2%}"
            )
            print(
                "수익률 표준편차: "
                f"{return_std:.2%}"
            )
            print(
                "최저 5일 수익률: "
                f"{worst_return:.2%}"
            )
            print(
                "최고 5일 수익률: "
                f"{best_return:.2%}"
            )

    result_df = pd.DataFrame(
        results
    )

    result_df = result_df.sort_values(
        by=[
            "threshold",
            "avg_return_5d",
            "success_rate_3pct",
            "total_trades",
        ],
        ascending=[
            True,
            False,
            False,
            False,
        ],
        na_position="last",
    )

    print("\n" + "#" * 80)
    print("Feature Pruning 최종 비교")
    print("#" * 80)
    print(result_df.to_string(index=False))

    result_path = (
        "ml/"
        "feature_pruning_result_all_thresholds.csv"
    )

    result_df.to_csv(
        result_path,
        index=False,
    )

    print(
        f"\nCSV 저장 완료: "
        f"{result_path}"
    )


if __name__ == "__main__":
    run_feature_pruning_backtest()