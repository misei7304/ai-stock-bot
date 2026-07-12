import sqlite3
import pandas as pd

DB_NAME = "stock_bot.db"


def analyze_ai_observation_score():
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query("""
        SELECT
            ticker,
            ai_date,
            ai_probability,
            market_state,
            return_1d,
            return_5d,
            return_20d
        FROM ai_observations
    """, conn)

    conn.close()

    print("\n" + "#" * 80)
    print("AI 후보 신뢰점수 분석")
    print("#" * 80)

    if df.empty:
        print("AI 후보 데이터가 없습니다.")
        return

    valid = df[df["return_5d"].notna()]

    if valid.empty:
        print("아직 5거래일 수익률 데이터가 부족합니다.")
        return

    win_rate = (valid["return_5d"] > 0).mean() * 100
    avg_return = valid["return_5d"].mean()

    score = 0
    score += win_rate * 0.6
    score += avg_return * 5

    print(f"분석 대상 후보 수: {len(valid)}개")
    print(f"5거래일 성공률: {win_rate:.2f}%")
    print(f"5거래일 평균수익률: {avg_return:.2f}%")
    print(f"AI 신뢰점수: {score:.2f}")

    if score >= 60:
        print("판단: AI 후보를 전략에 강하게 반영 가능")
    elif score >= 40:
        print("판단: AI 후보를 보조 점수로만 반영")
    else:
        print("판단: AI 후보 신뢰도 낮음, 관찰 유지")