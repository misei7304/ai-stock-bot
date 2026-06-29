import sqlite3
import pandas as pd

DB_NAME = "stock_bot.db"


def analyze_ai_observation_market_performance():
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query("""
        SELECT
            market_state,
            return_1d,
            return_5d,
            return_20d
        FROM ai_observations
    """, conn)

    conn.close()

    print("\n" + "#" * 80)
    print("AI 시장 상태별 성과 분석")
    print("#" * 80)

    if df.empty:
        print("AI 후보 데이터가 없습니다.")
        return

    groups = [
        ("상승장", df[df["market_state"] == "bull"]),
        ("약세장", df[df["market_state"] == "bear"])
    ]

    for label, group in groups:

        print(f"\n[{label}]")

        if group.empty:
            print("데이터 없음")
            continue

        print(f"후보 수: {len(group)}개")

        for period in [
            "return_1d",
            "return_5d",
            "return_20d"
        ]:

            valid = group[group[period].notna()]

            if valid.empty:
                print(f"{period}: 데이터 부족")
                continue

            win_rate = (valid[period] > 0).mean() * 100
            avg_return = valid[period].mean()

            print(
                f"{period}: "
                f"성공률 {win_rate:.2f}% | "
                f"평균수익률 {avg_return:.2f}%"
            )