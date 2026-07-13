from dataclasses import (
    asdict,
    dataclass,
)

import pandas as pd


DEFAULT_TRAIN_SIZE = 504

DEFAULT_VALIDATION_SIZE = 63

DEFAULT_STEP_SIZE = 63

DEFAULT_PURGE_SIZE = 5

DEFAULT_MINIMUM_WINDOW_COUNT = 3


@dataclass(
    frozen=True,
)
class WalkForwardWindow:
    window_number: int

    train_start_index: int
    train_end_index: int

    purge_start_index: int
    purge_end_index: int

    validation_start_index: int
    validation_end_index: int

    train_start_date: pd.Timestamp
    train_end_date: pd.Timestamp

    purge_start_date: pd.Timestamp
    purge_end_date: pd.Timestamp

    validation_start_date: pd.Timestamp
    validation_end_date: pd.Timestamp

    train_date_count: int
    purge_date_count: int
    validation_date_count: int

    def to_dict(
        self,
    ):
        result = asdict(
            self
        )

        date_keys = [
            "train_start_date",
            "train_end_date",
            "purge_start_date",
            "purge_end_date",
            "validation_start_date",
            "validation_end_date",
        ]

        for key in date_keys:
            result[
                key
            ] = str(
                result[
                    key
                ].date()
            )

        return result


def validate_walk_forward_parameters(
    train_size,
    validation_size,
    step_size,
    purge_size,
    minimum_window_count,
):
    parameter_values = {
        "train_size": train_size,
        "validation_size": (
            validation_size
        ),
        "step_size": step_size,
        "minimum_window_count": (
            minimum_window_count
        ),
    }

    for (
        parameter_name,
        parameter_value,
    ) in parameter_values.items():
        if not isinstance(
            parameter_value,
            int,
        ):
            raise TypeError(
                f"{parameter_name}는 "
                "정수여야 합니다."
            )

        if parameter_value <= 0:
            raise ValueError(
                f"{parameter_name}는 "
                "1 이상이어야 합니다."
            )

    if not isinstance(
        purge_size,
        int,
    ):
        raise TypeError(
            "purge_size는 "
            "정수여야 합니다."
        )

    if purge_size < 0:
        raise ValueError(
            "purge_size는 "
            "0 이상이어야 합니다."
        )

    return True


def normalize_unique_dates(
    dates,
):
    date_series = pd.Series(
        dates
    )

    if date_series.empty:
        raise ValueError(
            "Walk Forward 구간을 생성할 "
            "날짜가 없습니다."
        )

    normalized_dates = pd.to_datetime(
        date_series,
        errors="raise",
    )

    normalized_dates = (
        normalized_dates
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(
            drop=True
        )
    )

    if normalized_dates.empty:
        raise ValueError(
            "유효한 날짜가 없습니다."
        )

    return [
        pd.Timestamp(
            date
        )
        for date in normalized_dates
    ]


def calculate_possible_window_count(
    unique_date_count,
    train_size=DEFAULT_TRAIN_SIZE,
    validation_size=(
        DEFAULT_VALIDATION_SIZE
    ),
    step_size=DEFAULT_STEP_SIZE,
    purge_size=DEFAULT_PURGE_SIZE,
):
    validate_walk_forward_parameters(
        train_size=train_size,
        validation_size=(
            validation_size
        ),
        step_size=step_size,
        purge_size=purge_size,
        minimum_window_count=1,
    )

    first_validation_end_index = (
        train_size
        + purge_size
        + validation_size
        - 1
    )

    if (
        first_validation_end_index
        >= unique_date_count
    ):
        return 0

    remaining_date_count = (
        unique_date_count
        - first_validation_end_index
        - 1
    )

    return (
        1
        + (
            remaining_date_count
            // step_size
        )
    )


def generate_walk_forward_windows(
    dates,
    train_size=DEFAULT_TRAIN_SIZE,
    validation_size=(
        DEFAULT_VALIDATION_SIZE
    ),
    step_size=DEFAULT_STEP_SIZE,
    purge_size=DEFAULT_PURGE_SIZE,
    minimum_window_count=(
        DEFAULT_MINIMUM_WINDOW_COUNT
    ),
):
    validate_walk_forward_parameters(
        train_size=train_size,
        validation_size=(
            validation_size
        ),
        step_size=step_size,
        purge_size=purge_size,
        minimum_window_count=(
            minimum_window_count
        ),
    )

    unique_dates = (
        normalize_unique_dates(
            dates
        )
    )

    windows = []

    train_start_index = 0
    window_number = 1

    while True:
        train_end_index = (
            train_start_index
            + train_size
            - 1
        )

        purge_start_index = (
            train_end_index
            + 1
        )

        purge_end_index = (
            purge_start_index
            + purge_size
            - 1
        )

        validation_start_index = (
            train_end_index
            + purge_size
            + 1
        )

        validation_end_index = (
            validation_start_index
            + validation_size
            - 1
        )

        if (
            validation_end_index
            >= len(
                unique_dates
            )
        ):
            break

        if purge_size > 0:
            purge_start_date = (
                unique_dates[
                    purge_start_index
                ]
            )

            purge_end_date = (
                unique_dates[
                    purge_end_index
                ]
            )
        else:
            purge_start_date = (
                unique_dates[
                    train_end_index
                ]
            )

            purge_end_date = (
                unique_dates[
                    train_end_index
                ]
            )

        window = WalkForwardWindow(
            window_number=(
                window_number
            ),

            train_start_index=(
                train_start_index
            ),
            train_end_index=(
                train_end_index
            ),

            purge_start_index=(
                purge_start_index
            ),
            purge_end_index=(
                purge_end_index
            ),

            validation_start_index=(
                validation_start_index
            ),
            validation_end_index=(
                validation_end_index
            ),

            train_start_date=(
                unique_dates[
                    train_start_index
                ]
            ),
            train_end_date=(
                unique_dates[
                    train_end_index
                ]
            ),

            purge_start_date=(
                purge_start_date
            ),
            purge_end_date=(
                purge_end_date
            ),

            validation_start_date=(
                unique_dates[
                    validation_start_index
                ]
            ),
            validation_end_date=(
                unique_dates[
                    validation_end_index
                ]
            ),

            train_date_count=(
                train_size
            ),
            purge_date_count=(
                purge_size
            ),
            validation_date_count=(
                validation_size
            ),
        )

        windows.append(
            window
        )

        train_start_index += (
            step_size
        )

        window_number += 1

    if (
        len(
            windows
        )
        < minimum_window_count
    ):
        raise ValueError(
            "생성된 Walk Forward Window 수가 "
            "최소 기준보다 적습니다. "
            f"생성 수={len(windows)}, "
            f"최소 수={minimum_window_count}, "
            f"고유 날짜 수={len(unique_dates)}, "
            f"학습 크기={train_size}, "
            f"Purge 크기={purge_size}, "
            f"검증 크기={validation_size}, "
            f"이동 크기={step_size}"
        )

    return windows


def validate_walk_forward_dataframe(
    df,
):
    if not isinstance(
        df,
        pd.DataFrame,
    ):
        raise TypeError(
            "Walk Forward 대상 데이터는 "
            "DataFrame이어야 합니다."
        )

    if "Date" not in df.columns:
        raise ValueError(
            "Walk Forward 대상 데이터에 "
            "Date 컬럼이 없습니다."
        )

    if df.empty:
        raise ValueError(
            "Walk Forward 대상 데이터가 "
            "비어 있습니다."
        )

    return True


def get_walk_forward_dataframes(
    df,
    window,
):
    validate_walk_forward_dataframe(
        df
    )

    if not isinstance(
        window,
        WalkForwardWindow,
    ):
        raise TypeError(
            "window는 WalkForwardWindow "
            "형식이어야 합니다."
        )

    working_df = df.copy()

    working_df[
        "Date"
    ] = pd.to_datetime(
        working_df[
            "Date"
        ],
        errors="raise",
    )

    train_df = working_df[
        (
            working_df[
                "Date"
            ]
            >= window.train_start_date
        )
        & (
            working_df[
                "Date"
            ]
            <= window.train_end_date
        )
    ].copy()

    validation_df = working_df[
        (
            working_df[
                "Date"
            ]
            >= (
                window
                .validation_start_date
            )
        )
        & (
            working_df[
                "Date"
            ]
            <= (
                window
                .validation_end_date
            )
        )
    ].copy()

    if train_df.empty:
        raise ValueError(
            "Walk Forward 학습 데이터가 "
            "비어 있습니다. "
            f"Window={window.window_number}"
        )

    if validation_df.empty:
        raise ValueError(
            "Walk Forward 검증 데이터가 "
            "비어 있습니다. "
            f"Window={window.window_number}"
        )

    train_df = (
        train_df.sort_values(
            by=[
                "Date",
                "Ticker",
            ]
            if "Ticker"
            in train_df.columns
            else [
                "Date",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    validation_df = (
        validation_df.sort_values(
            by=[
                "Date",
                "Ticker",
            ]
            if "Ticker"
            in validation_df.columns
            else [
                "Date",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    train_dates = set(
        train_df[
            "Date"
        ].unique()
    )

    validation_dates = set(
        validation_df[
            "Date"
        ].unique()
    )

    overlapping_dates = (
        train_dates
        & validation_dates
    )

    if overlapping_dates:
        raise ValueError(
            "학습 구간과 검증 구간에 "
            "중복 날짜가 존재합니다."
        )

    return (
        train_df,
        validation_df,
    )


def print_walk_forward_summary(
    windows,
):
    if not windows:
        print(
            "생성된 Walk Forward "
            "Window가 없습니다."
        )

        return

    print(
        "\n"
        + "#"
        * 80
    )

    print(
        "Walk Forward Window 생성 결과"
    )

    print(
        "#"
        * 80
    )

    print(
        f"Window 수: "
        f"{len(windows)}"
    )

    for window in windows:
        print(
            "\n"
            f"[Window "
            f"{window.window_number}]"
        )

        print(
            "학습: "
            f"{window.train_start_date.date()} "
            f"~ "
            f"{window.train_end_date.date()} "
            f"({window.train_date_count}일)"
        )

        if (
            window.purge_date_count
            > 0
        ):
            print(
                "Purge: "
                f"{window.purge_start_date.date()} "
                f"~ "
                f"{window.purge_end_date.date()} "
                f"({window.purge_date_count}일)"
            )

        else:
            print(
                "Purge: 사용 안 함"
            )

        print(
            "검증: "
            f"{window.validation_start_date.date()} "
            f"~ "
            f"{window.validation_end_date.date()} "
            f"({window.validation_date_count}일)"
        )


if __name__ == "__main__":
    dataset_path = (
        "ml/training_dataset.csv"
    )

    dataset_df = pd.read_csv(
        dataset_path
    )

    dataset_df[
        "Date"
    ] = pd.to_datetime(
        dataset_df[
            "Date"
        ]
    )

    walk_forward_windows = (
        generate_walk_forward_windows(
            dates=dataset_df[
                "Date"
            ],
        )
    )

    print_walk_forward_summary(
        walk_forward_windows
    )

    first_train_df, (
        first_validation_df
    ) = (
        get_walk_forward_dataframes(
            df=dataset_df,
            window=(
                walk_forward_windows[
                    0
                ]
            ),
        )
    )

    last_train_df, (
        last_validation_df
    ) = (
        get_walk_forward_dataframes(
            df=dataset_df,
            window=(
                walk_forward_windows[
                    -1
                ]
            ),
        )
    )

    print(
        "\n"
        + "="
        * 80
    )

    print(
        "DataFrame 분리 테스트"
    )

    print(
        "="
        * 80
    )

    print(
        "첫 Window 학습 행 수: "
        f"{len(first_train_df):,}"
    )

    print(
        "첫 Window 검증 행 수: "
        f"{len(first_validation_df):,}"
    )

    print(
        "마지막 Window 학습 행 수: "
        f"{len(last_train_df):,}"
    )

    print(
        "마지막 Window 검증 행 수: "
        f"{len(last_validation_df):,}"
    )

    print(
        "\nWalk Forward 기본 테스트 통과"
    )
