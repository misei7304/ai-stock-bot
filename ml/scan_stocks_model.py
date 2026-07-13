import joblib
import pandas as pd
import yfinance as yf

from ml.ml_config import (
    AI_SIGNAL_THRESHOLD,
    TOP_AI_CANDIDATE_LIMIT,
)
from ml.ml_features import (
    FEATURES,
    add_features,
)
from ml.ml_tickers import ML_TICKERS


MODEL_PATH = "ml/trained_model.pkl"
FINAL_CANDIDATES_PATH = (
    "ml/final_candidates.csv"
)
SCAN_RESULTS_PATH = "ml/scan_results.csv"


def scan_stocks_model():
    model = joblib.load(MODEL_PATH)

    results = []

    for ticker in ML_TICKERS:
        try:
            df = yf.download(
                ticker,
                period="5y",
                progress=False,
            )

            if df.empty:
                print(
                    f"{ticker}: 데이터 없음"
                )
                continue

            if isinstance(
                df.columns,
                pd.MultiIndex,
            ):
                df.columns = (
                    df.columns.get_level_values(0)
                )

            df = add_features(df)

            latest_features_df = df.dropna(
                subset=FEATURES
            ).copy()

            if latest_features_df.empty:
                print(
                    f"{ticker}: "
                    "최신 feature 데이터 없음"
                )
                continue

            latest = (
                latest_features_df[
                    FEATURES
                ]
                .tail(1)
                .fillna(0)
            )

            latest_date = latest.index[0]

            latest_close = float(
                latest_features_df.loc[
                    latest_date,
                    "Close",
                ]
            )

            probability = float(
                model.predict_proba(
                    latest
                )[0][1]
            )

            results.append({
                "Ticker": ticker,
                "Date": (
                    latest_date.date()
                ),
                "Close": latest_close,
                "Probability": probability,
                "Signal": (
                    probability
                    >= AI_SIGNAL_THRESHOLD
                ),
            })

            print(
                f"{ticker}: "
                f"상승확률 "
                f"{probability:.2%}"
            )

        except Exception as error:
            print(
                f"{ticker}: "
                f"에러 - {error}"
            )

    result_df = pd.DataFrame(
        results
    )

    if result_df.empty:
        empty_candidates = pd.DataFrame(
            columns=[
                "Ticker",
                "Date",
                "Close",
                "Probability",
                "Signal",
            ]
        )

        empty_candidates.to_csv(
            FINAL_CANDIDATES_PATH,
            index=False,
        )

        print("\nAI 스캔 결과가 없습니다.")

        return []

    result_df = result_df.sort_values(
        by="Probability",
        ascending=False,
    )

    passed_df = (
        result_df[
            result_df["Signal"] == True
        ]
        .head(
            TOP_AI_CANDIDATE_LIMIT
        )
        .copy()
    )

    passed_df.to_csv(
        FINAL_CANDIDATES_PATH,
        index=False,
    )

    result_df.to_csv(
        SCAN_RESULTS_PATH,
        index=False,
    )

    print(
        "\nAI 신호 기준값: "
        f"{AI_SIGNAL_THRESHOLD:.2f}"
    )

    print(
        "최종 AI 후보 수: "
        f"{len(passed_df)}개"
    )

    print(
        "최종 후보 저장 완료: "
        f"{FINAL_CANDIDATES_PATH}"
    )

    print(
        "전체 결과 저장 완료: "
        f"{SCAN_RESULTS_PATH}"
    )

    return passed_df.to_dict(
        orient="records"
    )


if __name__ == "__main__":
    pd.set_option(
        "display.max_columns",
        None,
    )

    pd.set_option(
        "display.width",
        200,
    )

    print("\n" + "#" * 80)
    print("AI 종목 스캔")
    print("#" * 80)

    scan_results = scan_stocks_model()

    if not scan_results:
        print("AI 기준 통과 종목이 없습니다.")

    else:
        print("\n최종 AI 후보")

        for result in scan_results:
            print(
                f"{result['Ticker']} | "
                f"확률 "
                f"{result['Probability']:.2%} | "
                f"기준일 "
                f"{result['Date']} | "
                f"기준가 "
                f"{result['Close']:,.0f}원"
            )