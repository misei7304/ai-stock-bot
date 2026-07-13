import pandas as pd

from ml.feature_subset_backtest import (
    FEATURE_SUBSETS,
    THRESHOLDS,
)

from ml.ml_model import create_model

DATASET_PATH = (
    "ml/training_dataset.csv"
)

RESULT_PATH = (
    "ml/feature_subset_trade_result.csv"
)

HOLDING_DAYS = 5

TOP_N_SIGNALS = 3

MAX_OPEN_POSITIONS = 3

START_MONEY = 1_000_000

def validate_dataset(df):

    required = {
        "Date",
        "Ticker",
        "Close",
        "Future_Return_5D",
        "Target",
    }

    for features in FEATURE_SUBSETS.values():
        required.update(features)

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "필요한 컬럼이 없습니다: "
            + ", ".join(sorted(missing))
        )
    
def select_non_overlapping_trades(
    signal_df,
):
    if signal_df.empty:
        return pd.DataFrame()

    signal_df = signal_df.sort_values(
        by=[
            "Date",
            "Probability",
        ],
        ascending=[
            True,
            False,
        ],
    ).copy()

    selected_trades = []

    next_available_date = {}

    for trade_date, daily_df in (
        signal_df.groupby(
            "Date",
            sort=True,
        )
    ):
        daily_df = daily_df.sort_values(
            by="Probability",
            ascending=False,
        )

        daily_selected_count = 0

        for _, row in daily_df.iterrows():
            ticker = row["Ticker"]

            available_date = (
                next_available_date.get(
                    ticker
                )
            )

            if (
                available_date is not None
                and trade_date
                < available_date
            ):
                continue

            selected_trades.append(
                row.to_dict()
            )

            next_available_date[
                ticker
            ] = (
                trade_date
                + pd.offsets.BDay(
                    HOLDING_DAYS
                )
            )

            daily_selected_count += 1

            if (
                daily_selected_count
                >= TOP_N_SIGNALS
            ):
                break

    if not selected_trades:
        return pd.DataFrame()

    return pd.DataFrame(
        selected_trades
    )

def add_exit_date(
    trade_df,
):
    if trade_df.empty:
        return trade_df

    trade_df = trade_df.copy()

    trade_df["Exit_Date"] = (
        trade_df["Date"]
        + pd.offsets.BDay(
            HOLDING_DAYS
        )
    )

    return trade_df

def simulate_portfolio(
    trade_df,
):
    if trade_df.empty:
        return {
            "portfolio_history": [],
            "executed_trades": pd.DataFrame(),
            "final_money": START_MONEY,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "skipped_trade_count": 0,
        }

    required_columns = {
        "Date",
        "Exit_Date",
        "Ticker",
        "Probability",
        "Future_Return_5D",
    }

    missing_columns = (
        required_columns
        - set(trade_df.columns)
    )

    if missing_columns:
        raise ValueError(
            "포트폴리오 시뮬레이션에 필요한 컬럼이 없습니다: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    trade_df = trade_df.copy()

    trade_df["Date"] = pd.to_datetime(
        trade_df["Date"]
    )

    trade_df["Exit_Date"] = pd.to_datetime(
        trade_df["Exit_Date"]
    )

    trade_df = trade_df.sort_values(
        by=[
            "Date",
            "Probability",
        ],
        ascending=[
            True,
            False,
        ],
    )

    cash = float(
        START_MONEY
    )

    open_positions = []
    executed_trades = []
    portfolio_history = []

    skipped_trade_count = 0

    all_event_dates = sorted(
        set(trade_df["Date"])
        | set(trade_df["Exit_Date"])
    )

    for current_date in all_event_dates:
        remaining_positions = []
        exited_position_count = 0

        for position in open_positions:
            if (
                position["Exit_Date"]
                <= current_date
            ):
                exit_value = (
                    position[
                        "Invested_Amount"
                    ]
                    * (
                        1
                        + position[
                            "Future_Return_5D"
                        ]
                    )
                )

                cash += exit_value

                completed_position = {
                    **position,
                    "Exit_Value": float(
                        exit_value
                    ),
                    "Profit_Amount": float(
                        exit_value
                        - position[
                            "Invested_Amount"
                        ]
                    ),
                }

                executed_trades.append(
                    completed_position
                )

                exited_position_count += 1

            else:
                remaining_positions.append(
                    position
                )

        open_positions = (
            remaining_positions
        )

        entry_candidates = trade_df[
            trade_df["Date"]
            == current_date
        ].copy()

        if not entry_candidates.empty:
            entry_candidates = (
                entry_candidates
                .sort_values(
                    by="Probability",
                    ascending=False,
                )
            )

            available_slots = (
                MAX_OPEN_POSITIONS
                - len(open_positions)
            )

            if available_slots <= 0:
                skipped_trade_count += len(
                    entry_candidates
                )

            else:
                selected_candidates = (
                    entry_candidates
                    .head(
                        available_slots
                    )
                )

                skipped_trade_count += (
                    len(entry_candidates)
                    - len(
                        selected_candidates
                    )
                )

                candidate_count = len(
                    selected_candidates
                )

                if (
                    candidate_count > 0
                    and cash > 0
                ):
                    money_per_position = (
                        cash
                        / candidate_count
                    )

                    cash -= (
                        money_per_position
                        * candidate_count
                    )

                    for _, trade in (
                        selected_candidates
                        .iterrows()
                    ):
                        position = {
                            "Date": trade["Date"],
                            "Exit_Date": (
                                trade[
                                    "Exit_Date"
                                ]
                            ),
                            "Ticker": (
                                trade["Ticker"]
                            ),
                            "Probability": float(
                                trade[
                                    "Probability"
                                ]
                            ),
                            "Future_Return_5D": float(
                                trade[
                                    "Future_Return_5D"
                                ]
                            ),
                            "Invested_Amount": float(
                                money_per_position
                            ),
                        }

                        if "Fold" in trade.index:
                            position["Fold"] = (
                                trade["Fold"]
                            )

                        open_positions.append(
                            position
                        )

        invested_amount = sum(
            position[
                "Invested_Amount"
            ]
            for position
            in open_positions
        )

        estimated_equity = (
            cash
            + invested_amount
        )

        portfolio_history.append({
            "Date": current_date,
            "Cash": float(cash),
            "Open_Position_Count": int(
                len(open_positions)
            ),
            "Invested_Amount": float(
                invested_amount
            ),
            "Estimated_Equity": float(
                estimated_equity
            ),
            "Exited_Position_Count": int(
                exited_position_count
            ),
        })

    if open_positions:
        final_date = max(
            position["Exit_Date"]
            for position
            in open_positions
        )

        final_exit_count = len(
            open_positions
        )

        for position in open_positions:
            exit_value = (
                position[
                    "Invested_Amount"
                ]
                * (
                    1
                    + position[
                        "Future_Return_5D"
                    ]
                )
            )

            cash += exit_value

            completed_position = {
                **position,
                "Exit_Value": float(
                    exit_value
                ),
                "Profit_Amount": float(
                    exit_value
                    - position[
                        "Invested_Amount"
                    ]
                ),
            }

            executed_trades.append(
                completed_position
            )

        portfolio_history.append({
            "Date": final_date,
            "Cash": float(cash),
            "Open_Position_Count": 0,
            "Invested_Amount": 0.0,
            "Estimated_Equity": float(
                cash
            ),
            "Exited_Position_Count": int(
                final_exit_count
            ),
        })

    executed_trade_df = pd.DataFrame(
        executed_trades
    )

    equity_values = [
        float(START_MONEY),
        *[
            float(
                history[
                    "Estimated_Equity"
                ]
            )
            for history
            in portfolio_history
        ],
    ]

    equity_series = pd.Series(
        equity_values,
        dtype=float,
    )

    running_max = (
        equity_series.cummax()
    )

    drawdown = (
        equity_series
        / running_max
        - 1
    )

    final_money = float(
        cash
    )

    return {
        "portfolio_history": (
            portfolio_history
        ),
        "executed_trades": (
            executed_trade_df
        ),
        "final_money": (
            final_money
        ),
        "total_return": float(
            final_money
            / START_MONEY
            - 1
        ),
        "max_drawdown": float(
            drawdown.min()
        ),
        "skipped_trade_count": int(
            skipped_trade_count
        ),
    }

def calculate_trade_metrics(
    trade_df,
):
    if trade_df.empty:
        return {
            "trade_count": 0,
            "candidate_trade_count": 0,
            "skipped_trade_count": 0,
            "success_rate_3pct": None,
            "profitable_rate": None,
            "average_return": None,
            "median_return": None,
            "return_std": None,
            "best_trade": None,
            "worst_trade": None,
            "total_return": 0.0,
            "final_money": (
                START_MONEY
            ),
            "max_drawdown": 0.0,
        }

    trade_df = trade_df.copy()

    if (
        "Exit_Date"
        not in trade_df.columns
    ):
        trade_df = add_exit_date(
            trade_df
        )

    portfolio_result = (
        simulate_portfolio(
            trade_df
        )
    )

    executed_trade_df = (
        portfolio_result[
            "executed_trades"
        ]
    )

    if executed_trade_df.empty:
        return {
            "trade_count": 0,
            "candidate_trade_count": int(
                len(trade_df)
            ),
            "skipped_trade_count": int(
                portfolio_result[
                    "skipped_trade_count"
                ]
            ),
            "success_rate_3pct": None,
            "profitable_rate": None,
            "average_return": None,
            "median_return": None,
            "return_std": None,
            "best_trade": None,
            "worst_trade": None,
            "total_return": float(
                portfolio_result[
                    "total_return"
                ]
            ),
            "final_money": float(
                portfolio_result[
                    "final_money"
                ]
            ),
            "max_drawdown": float(
                portfolio_result[
                    "max_drawdown"
                ]
            ),
        }

    returns = (
        executed_trade_df[
            "Future_Return_5D"
        ]
        .astype(float)
    )

    return {
        "trade_count": int(
            len(
                executed_trade_df
            )
        ),
        "candidate_trade_count": int(
            len(trade_df)
        ),
        "skipped_trade_count": int(
            portfolio_result[
                "skipped_trade_count"
            ]
        ),
        "success_rate_3pct": float(
            (
                returns >= 0.03
            ).mean()
        ),
        "profitable_rate": float(
            (
                returns > 0
            ).mean()
        ),
        "average_return": float(
            returns.mean()
        ),
        "median_return": float(
            returns.median()
        ),
        "return_std": float(
            returns.std()
        ),
        "best_trade": float(
            returns.max()
        ),
        "worst_trade": float(
            returns.min()
        ),
        "total_return": float(
            portfolio_result[
                "total_return"
            ]
        ),
        "final_money": float(
            portfolio_result[
                "final_money"
            ]
        ),
        "max_drawdown": float(
            portfolio_result[
                "max_drawdown"
            ]
        ),
    }

def run_single_trade_backtest(
    df,
    unique_dates,
    train_window,
    test_window,
    step_size,
    subset_name,
    feature_list,
    threshold,
):
    print("\n" + "=" * 80)
    print(
        f"거래 백테스트: "
        f"{subset_name}"
    )
    print(
        f"Feature 수: "
        f"{len(feature_list)}"
    )
    print(
        f"기준값: "
        f"{threshold:.2f}"
    )
    print("=" * 80)

    selected_trade_frames = []

    fold = 1

    for start in range(
        0,
        (
            len(unique_dates)
            - train_window
            - test_window
        ),
        step_size,
    ):
        train_start = (
            unique_dates[start]
        )

        train_end = unique_dates[
            start
            + train_window
            - 1
        ]

        test_start = unique_dates[
            start
            + train_window
        ]

        test_end = unique_dates[
            start
            + train_window
            + test_window
            - 1
        ]

        train_df = df[
            (
                df["Date"]
                >= train_start
            )
            & (
                df["Date"]
                <= train_end
            )
        ].copy()

        test_df = df[
            (
                df["Date"]
                >= test_start
            )
            & (
                df["Date"]
                <= test_end
            )
        ].copy()

        X_train = (
            train_df[
                feature_list
            ]
            .fillna(0)
        )

        y_train = (
            train_df["Target"]
        )

        X_test = (
            test_df[
                feature_list
            ]
            .fillna(0)
        )

        if (
            X_train.empty
            or X_test.empty
            or y_train.nunique() < 2
        ):
            print(
                f"Fold {fold} | "
                "검증 생략"
            )

            fold += 1
            continue

        model = create_model()

        model.fit(
            X_train,
            y_train,
        )

        test_df[
            "Probability"
        ] = model.predict_proba(
            X_test
        )[:, 1]

        signal_df = test_df[
            test_df["Probability"]
            >= threshold
        ].copy()

        selected_df = (
            select_non_overlapping_trades(
                signal_df
            )
        )

        if selected_df.empty:
            print(
                f"Fold {fold} | "
                "선택 거래 없음"
            )

            fold += 1
            continue

        selected_df[
            "Fold"
        ] = fold

        selected_trade_frames.append(
            selected_df
        )

        fold_metrics = (
            calculate_trade_metrics(
                selected_df
            )
        )

        print(
            f"Fold {fold} | "
            f"거래 "
            f"{fold_metrics['trade_count']}회 | "
            f"+3% 성공률 "
            f"{fold_metrics['success_rate_3pct']:.2%} | "
            f"평균수익 "
            f"{fold_metrics['average_return']:.2%}"
        )

        fold += 1

    if not selected_trade_frames:
        final_trades = pd.DataFrame()

    else:
        final_trades = pd.concat(
            selected_trade_frames,
            ignore_index=True,
        )

        final_trades = (
            select_non_overlapping_trades(
                final_trades
            )
        )

    final_trades = add_exit_date(
        final_trades
    )

    metrics = calculate_trade_metrics(
        final_trades
    )

    result = {
        "subset_name": subset_name,
        "threshold": threshold,
        "feature_count": len(
            feature_list
        ),
        "holding_days": HOLDING_DAYS,
        "top_n_signals": TOP_N_SIGNALS,
        "max_open_positions": (
            MAX_OPEN_POSITIONS
        ),
        **metrics,
    }

    print("\n요약")
    print(
        f"최종 거래 수: "
        f"{result['trade_count']}"
    )
    print(
        f"후보 거래 수: "
        f"{result['candidate_trade_count']}"
    )

    print(
        f"자금 또는 보유 한도로 제외: "
        f"{result['skipped_trade_count']}"
    )

    if result["trade_count"] > 0:
        print(
            "+3% 성공률: "
            f"{result['success_rate_3pct']:.2%}"
        )
        print(
            "수익 발생률: "
            f"{result['profitable_rate']:.2%}"
        )
        print(
            "평균 거래 수익률: "
            f"{result['average_return']:.2%}"
        )
        print(
            "누적 수익률: "
            f"{result['total_return']:.2%}"
        )
        print(
            "최종 자산: "
            f"{result['final_money']:,.0f}원"
        )
        print(
            "최대 낙폭: "
            f"{result['max_drawdown']:.2%}"
        )

    return result

def run_feature_subset_trade_backtest():
    df = pd.read_csv(
        DATASET_PATH
    )

    validate_dataset(
        df
    )

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    df = df.sort_values(
        by=[
            "Date",
            "Ticker",
        ]
    )

    unique_dates = sorted(
        df["Date"].unique()
    )

    train_window = int(
        len(unique_dates) * 0.6
    )

    test_window = int(
        len(unique_dates) * 0.1
    )

    step_size = test_window

    if (
        train_window <= 0
        or test_window <= 0
        or step_size <= 0
    ):
        raise ValueError(
            "Walk-Forward 검증 데이터가 "
            "부족합니다."
        )

    print("\n" + "#" * 80)
    print("Feature Subset 실제 거래 백테스트")
    print("#" * 80)

    results = []

    for (
        subset_name,
        feature_list,
    ) in FEATURE_SUBSETS.items():
        for threshold in THRESHOLDS:
            result = (
                run_single_trade_backtest(
                    df=df,
                    unique_dates=unique_dates,
                    train_window=train_window,
                    test_window=test_window,
                    step_size=step_size,
                    subset_name=subset_name,
                    feature_list=feature_list,
                    threshold=threshold,
                )
            )

            results.append(
                result
            )

    result_df = pd.DataFrame(
        results
    )

    result_df = result_df.sort_values(
        by=[
            "total_return",
            "max_drawdown",
            "success_rate_3pct",
            "trade_count",
        ],
        ascending=[
            False,
            False,
            False,
            False,
        ],
        na_position="last",
    ).reset_index(
        drop=True
    )

    result_df[
        "rank"
    ] = (
        result_df.index + 1
    )

    output_columns = [
        "rank",
        "subset_name",
        "threshold",
        "feature_count",
        "holding_days",
        "top_n_signals",
        "max_open_positions",
        "candidate_trade_count",
        "trade_count",
        "skipped_trade_count",
        "success_rate_3pct",
        "profitable_rate",
        "average_return",
        "median_return",
        "return_std",
        "best_trade",
        "worst_trade",
        "total_return",
        "final_money",
        "max_drawdown",
    ]

    result_df = result_df[
        output_columns
    ]

    result_df.to_csv(
        RESULT_PATH,
        index=False,
    )

    print("\n" + "#" * 80)
    print("실제 거래 백테스트 최종 비교")
    print("#" * 80)

    print(
        result_df.to_string(
            index=False
        )
    )

    print(
        "\nCSV 저장 완료: "
        f"{RESULT_PATH}"
    )

    return result_df


if __name__ == "__main__":
    run_feature_subset_trade_backtest()