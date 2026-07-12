import sqlite3
import pandas as pd


DB_NAME = "stock_bot.db"


def analyze_ai_observation_performance():
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query("""
        SELECT
            ticker,
            ai_date,
            ai_probability,
            current_return,
            return_1d,
            return_5d,
            return_20d
        FROM ai_observations
        WHERE current_return IS NOT NULL
    """, conn)

    conn.close()

    print("\n" + "#" * 80)
    print("AI 후보 성과 분석")
    print("#" * 80)

    if df.empty:
        print("AI 후보 성과 데이터가 아직 없습니다.")
        return

    total_count = len(df)
    win_count = len(df[df["current_return"] > 0])
    win_rate = win_count / total_count * 100
    avg_return = df["current_return"].mean()

    print(f"AI 후보 수: {total_count}개")
    print(f"수익중: {win_count}개")
    print(f"성공률: {win_rate:.2f}%")
    print(f"평균 현재수익률: {avg_return:.2f}%")

    high_prob_df = df[df["ai_probability"] >= 0.70]

    print("\n[AI 확률 70% 이상]")
    if high_prob_df.empty:
        print("데이터 없음")
    else:
        high_win_count = len(high_prob_df[high_prob_df["current_return"] > 0])
        high_win_rate = high_win_count / len(high_prob_df) * 100
        high_avg_return = high_prob_df["current_return"].mean()

        print(f"후보 수: {len(high_prob_df)}개")
        print(f"성공률: {high_win_rate:.2f}%")
        print(f"평균 현재수익률: {high_avg_return:.2f}%")

    print("\n종목별 AI 성과")

    stock_summary = df.groupby("ticker").agg(
        count=("ticker", "count"),
        avg_probability=("ai_probability", "mean"),
        avg_return=("current_return", "mean")
    ).reset_index()

    stock_summary = stock_summary.sort_values(
        by="avg_return",
        ascending=False
    )

    for _, row in stock_summary.iterrows():
        print(
            f"{row['ticker']} | "
            f"추천수 {int(row['count'])}회 | "
            f"평균AI확률 {row['avg_probability']:.2%} | "
            f"평균수익률 {row['avg_return']:.2f}%"
        )