import joblib
import pandas as pd

from datetime import (
    datetime,
)

from sklearn.metrics import (
    accuracy_score,
    classification_report,
)

from ml.ml_model import create_model
from ml.selected_model_config import (
    get_selected_model_config,
)


DATASET_PATH = (
    "ml/training_dataset.csv"
)

MODEL_PATH = (
    "ml/trained_model.pkl"
)


def validate_training_dataset(
    df,
    features,
):
    required_columns = {
        "Date",
        "Target",
        *features,
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "학습 데이터셋에 필요한 "
            "컬럼이 없습니다: "
            + ", ".join(
                sorted(
                    missing_columns
                )
            )
        )


def train_model():
    config = (
        get_selected_model_config()
    )

    features = config[
        "features"
    ]

    threshold = config[
        "threshold"
    ]

    df = pd.read_csv(
        DATASET_PATH
    )

    validate_training_dataset(
        df=df,
        features=features,
    )

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    df = df.sort_values(
        by=[
            "Date",
            "Ticker",
        ]
    ).reset_index(
        drop=True
    )

    unique_dates = sorted(
        df["Date"].unique()
    )

    split_index = int(
        len(unique_dates)
        * 0.8
    )

    if (
        split_index <= 0
        or split_index
        >= len(unique_dates)
    ):
        raise ValueError(
            "날짜 기준 학습·검증 분할을 "
            "생성할 수 없습니다."
        )

    split_date = unique_dates[
        split_index
    ]

    train_df = df[
        df["Date"]
        < split_date
    ].copy()

    test_df = df[
        df["Date"]
        >= split_date
    ].copy()

    X_train = (
        train_df[
            features
        ]
        .fillna(0)
    )

    y_train = train_df[
        "Target"
    ]

    X_test = (
        test_df[
            features
        ]
        .fillna(0)
    )

    y_test = test_df[
        "Target"
    ]

    if X_train.empty:
        raise ValueError(
            "학습 데이터가 없습니다."
        )

    if X_test.empty:
        raise ValueError(
            "검증 데이터가 없습니다."
        )

    if (
        y_train.nunique()
        < 2
    ):
        raise ValueError(
            "학습 데이터의 Target 클래스가 "
            "2개 미만입니다."
        )

    model = create_model()

    model.fit(
        X_train,
        y_train,
    )

    probabilities = (
        model.predict_proba(
            X_test
        )[:, 1]
    )

    predictions = (
        probabilities
        >= threshold
    ).astype(int)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    signal_count = int(
        predictions.sum()
    )

    actual_positive_count = int(
        y_test.sum()
    )

    signal_mask = (
        predictions == 1
    )

    if signal_count > 0:
        signal_success_rate = float(
            y_test[
                signal_mask
            ].mean()
        )
    else:
        signal_success_rate = None

    print(
        "\n"
        + "#"
        * 80
    )
    print(
        "선택된 통합 모델 학습 결과"
    )
    print(
        "#"
        * 80
    )

    print(
        f"Feature Subset: "
        f"{config['subset_name']}"
    )

    print(
        f"Feature 수: "
        f"{len(features)}"
    )

    print(
        "Features: "
        + ", ".join(
            features
        )
    )

    print(
        f"Threshold: "
        f"{threshold:.2f}"
    )

    print(
        f"전체 데이터 수: "
        f"{len(df):,}"
    )

    print(
        f"학습 데이터 수: "
        f"{len(X_train):,}"
    )

    print(
        f"검증 데이터 수: "
        f"{len(X_test):,}"
    )

    print(
        f"학습 기간: "
        f"{train_df['Date'].min().date()} "
        f"~ "
        f"{train_df['Date'].max().date()}"
    )

    print(
        f"검증 기간: "
        f"{test_df['Date'].min().date()} "
        f"~ "
        f"{test_df['Date'].max().date()}"
    )

    print(
        f"예측 매수 신호 수: "
        f"{signal_count:,}"
    )

    print(
        f"실제 +3% Target 수: "
        f"{actual_positive_count:,}"
    )

    print(
        f"Threshold 기준 정확도: "
        f"{accuracy:.2%}"
    )

    if signal_success_rate is None:
        print(
            "매수 신호 +3% 성공률: "
            "신호 없음"
        )
    else:
        print(
            "매수 신호 +3% 성공률: "
            f"{signal_success_rate:.2%}"
        )

    print(
        "\n=== 상세 결과 ==="
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    model_data = {
        "model": model,

        "subset_name": (
            config["subset_name"]
        ),

        "features": list(
            features
        ),

        "threshold": float(
            threshold
        ),

        "holding_days": int(
            config["holding_days"]
        ),

        "top_n_signals": int(
            config["top_n_signals"]
        ),

        "max_open_positions": int(
            config["max_open_positions"]
        ),

        "trained_at": datetime.now().isoformat(
            timespec="seconds"
        ),

        "train_start_date": str(
            train_df["Date"]
            .min()
            .date()
        ),

        "train_end_date": str(
            train_df["Date"]
            .max()
            .date()
        ),

        "validation_start_date": str(
            test_df["Date"]
            .min()
            .date()
        ),

        "validation_end_date": str(
            test_df["Date"]
            .max()
            .date()
        ),

        "model_params": model.get_params(),
    }

    joblib.dump(
        model_data,
        MODEL_PATH,
    )

    print(
        "\n모델 저장 완료: "
        f"{MODEL_PATH}"
    )

    print(
        f"학습 시각: "
        f"{model_data['trained_at']}"
    )

    print(
        "모델 파라미터:"
    )

    for key, value in (
        model_data[
            "model_params"
        ]
        .items()
    ):
        print(
            f"  {key}: {value}"
        )

    return model_data


if __name__ == "__main__":
    train_model()