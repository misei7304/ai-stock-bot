import sqlite3
import pandas as pd


DB_NAME = "stock_bot.db"


def analyze_ai_observation_signal_performance():
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query("""
        SELECT
            ticker,
            ai_date,
            ai_probability,
            return_1d,
            return_5d,
            return_20d
        FROM ai_observations
    """, conn)

    conn.close()

    print("\n" + "#" * 80)
    print("AI 확률 구간별 성과 분석")
    print("#" * 80)

    if df.empty:
        print("AI 후보 데이터가 없습니다.")
        return

    ranges = [
        ("70% 이상", df[df["ai_probability"] >= 0.70]),
        ("65% ~ 70%", df[(df["ai_probability"] >= 0.65) & (df["ai_probability"] < 0.70)]),
        ("60% ~ 65%", df[(df["ai_probability"] >= 0.60) & (df["ai_probability"] < 0.65)]),
        ("60% 미만", df[df["ai_probability"] < 0.60]),
    ]

    for label, group in ranges:
        print(f"\n[{label}]")

        if group.empty:
            print("데이터 없음")
            continue

        print(f"후보 수: {len(group)}개")

        for period in ["return_1d", "return_5d", "return_20d"]:
            valid = group[group[period].notna()]

            if valid.empty:
                print(f"{period}: 데이터 부족")
                continue

            win_count = len(valid[valid[period] > 0])
            win_rate = win_count / len(valid) * 100
            avg_return = valid[period].mean()

            print(
                f"{period}: "
                f"성공률 {win_rate:.2f}% | "
                f"평균수익률 {avg_return:.2f}%"
            )