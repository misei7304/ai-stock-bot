import joblib
import pandas as pd

from ml.ml_model import (
    create_model,
)

MODEL_PATH = (
    "ml/trained_model.pkl"
)

DATASET_PATH = (
    "ml/training_dataset.csv"
)

SIGNAL_PATH = (
    "ml/walk_forward_signals.csv"
)

def load_trained_model_data():
    model_data = joblib.load(
        MODEL_PATH
    )

    if not isinstance(
        model_data,
        dict,
    ):
        raise ValueError(
            "저장된 모델 형식이 올바르지 않습니다. "
            "ml/train_model.py를 다시 실행하세요."
        )

    required_keys = {
        "model",
        "subset_name",
        "features",
        "threshold",
        "holding_days",
        "top_n_signals",
        "max_open_positions",
    }

    missing_keys = (
        required_keys
        - set(
            model_data.keys()
        )
    )

    if missing_keys:
        raise ValueError(
            "저장된 모델 설정이 부족합니다: "
            + ", ".join(
                sorted(
                    missing_keys
                )
            )
        )

    if not model_data[
        "features"
    ]:
        raise ValueError(
            "저장된 Feature 목록이 "
            "비어 있습니다."
        )

    return model_data


def walk_forward_backtest():
    model_data = (
        load_trained_model_data()
    )

    features = list(
        model_data["features"]
    )

    selected_threshold = float(
        model_data["threshold"]
    )

    subset_name = model_data[
        "subset_name"
    ]

    holding_days = int(
        model_data["holding_days"]
    )

    top_n_signals = int(
        model_data["top_n_signals"]
    )

    max_open_positions = int(
        model_data["max_open_positions"]
    )

    df = pd.read_csv(DATASET_PATH)

    required_columns = {
        "Date",
        "Ticker",
        "Future_Return_5D",
        "Target",
        *features,
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Walk-Forward 데이터에 필요한 "
            "컬럼이 없습니다: "
            + ", ".join(
                sorted(
                    missing_columns
                )
            )
        )

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date")

    unique_dates = sorted(df["Date"].unique())

    train_window = int(len(unique_dates) * 0.6)
    test_window = int(len(unique_dates) * 0.1)
    step_size = test_window

    thresholds = sorted(
        {
            0.50,
            0.60,
            0.70,
            0.80,
            selected_threshold,
        }
    )

    all_signals = []
    summary_rows = []

    print("\n" + "#" * 80)
    print("Walk-Forward 반복 검증")
    print("#" * 80)

    print(
        f"Feature Subset: "
        f"{subset_name}"
    )

    print(
        f"Feature 수: "
        f"{len(features)}"
    )

    print(
        f"Threshold: "
        f"{selected_threshold:.2f}"
    )

    print(
        f"Holding Days: "
        f"{holding_days}"
    )

    print(
        f"Top N Signals: "
        f"{top_n_signals}"
    )

    print(
        f"Max Open Positions: "
        f"{max_open_positions}"
    )

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

        X_train = (
            train_df[
                features
            ]
            .fillna(0)
        )

        y_train = (
            train_df[
                "Target"
            ]
        )

        X_test = (
            test_df[
                features
            ]
            .fillna(0)
        )

        if X_train.empty:
            print(
                f"Fold {fold} | "
                "학습 데이터 없음"
            )

            fold += 1
            continue

        if X_test.empty:
            print(
                f"Fold {fold} | "
                "검증 데이터 없음"
            )

            fold += 1
            continue

        if (
            y_train.nunique()
            < 2
        ):
            print(
                f"Fold {fold} | "
                "학습 Target 클래스 부족"
            )

            fold += 1
            continue

        model = create_model()

        model.fit(
            X_train,
            y_train,
        )

        test_df["Probability"] = model.predict_proba(X_test)[:, 1]
        test_df["Fold"] = fold

        print("\n" + "-" * 80)
        print(f"Fold {fold}")
        print(f"학습 기간: {pd.Timestamp(train_start).date()} ~ {pd.Timestamp(train_end).date()}")
        print(f"검증 기간: {pd.Timestamp(test_start).date()} ~ {pd.Timestamp(test_end).date()}")

        for threshold in thresholds:
            signal_df = test_df[test_df["Probability"] >= threshold].copy()

            if signal_df.empty:
                print(f"기준값 {threshold:.2f}: 신호 없음")

                summary_rows.append({
                    "fold": fold,
                    "threshold": threshold,
                    "trade_count": 0,
                    "win_rate": None,
                    "avg_return_5d": None,
                    "median_return_5d": None,
                })

                continue

            trade_count = len(signal_df)
            win_rate = (signal_df["Future_Return_5D"] >= 0.03).mean()
            avg_return = signal_df["Future_Return_5D"].mean()
            median_return = signal_df["Future_Return_5D"].median()

            print(f"기준값 {threshold:.2f} | 신호 {trade_count}개 | 성공률 {win_rate:.2%} | 평균수익 {avg_return:.2%}")

            summary_rows.append({
                "fold": fold,
                "threshold": threshold,
                "trade_count": trade_count,
                "win_rate": win_rate,
                "avg_return_5d": avg_return,
                "median_return_5d": median_return,
            })

            signal_df["Threshold"] = threshold
            
            signal_df["Subset_Name"] = subset_name

            signal_df["Holding_Days"] = holding_days

            signal_df["Top_N_Signals"] = top_n_signals

            signal_df["Max_Open_Positions"] = (
                max_open_positions
            )
            all_signals.append(signal_df)

        fold += 1

    summary_df = pd.DataFrame(summary_rows)

    print("\n" + "#" * 80)
    print("Walk-Forward 전체 요약")
    print("#" * 80)

    for threshold in thresholds:
        target = summary_df[
            (summary_df["threshold"] == threshold) &
            (summary_df["trade_count"] > 0)
        ]

        if target.empty:
            print(f"\n기준값 {threshold:.2f}: 전체 신호 없음")
            continue

        total_trades = target["trade_count"].sum()
        avg_win_rate = target["win_rate"].mean()
        avg_return = target["avg_return_5d"].mean()
        median_return = target["median_return_5d"].mean()

        print(f"\n기준값 {threshold:.2f}")
        print(f"총 신호 수: {total_trades}")
        print(f"평균 성공률: {avg_win_rate:.2%}")
        print(f"평균 5일 수익률: {avg_return:.2%}")
        print(f"중앙값 평균 5일 수익률: {median_return:.2%}")

    if all_signals:
        final_signals = pd.concat(all_signals)
        final_signals.to_csv(SIGNAL_PATH, index=False)
        print(f"\nCSV 저장 완료: {SIGNAL_PATH}")
    else:
        print("\n저장할 신호가 없습니다.")


if __name__ == "__main__":
    walk_forward_backtest()