import sqlite3
from datetime import datetime


DB_NAME = "stock_bot.db"


def initialize_ai_observation_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            ai_date TEXT,
            ai_close REAL,
            ai_probability REAL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_ai_observations(ai_candidates):
    initialize_ai_observation_table()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    saved_count = 0
    skipped_count = 0

    for candidate in ai_candidates:
        ticker = candidate["ticker"]
        ai_date = str(candidate["ai_date"])

        cursor.execute("""
            SELECT COUNT(*)
            FROM ai_observations
            WHERE ticker = ?
            AND ai_date = ?
        """, (ticker, ai_date))

        exists = cursor.fetchone()[0]

        if exists > 0:
            skipped_count += 1
            continue

        cursor.execute("""
            INSERT INTO ai_observations (
                ticker,
                ai_date,
                ai_close,
                ai_probability,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            ticker,
            ai_date,
            float(candidate["ai_close"]),
            float(candidate["ai_probability"]),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        saved_count += 1

    conn.commit()
    conn.close()

    print(f"AI 후보 DB 저장 완료: 신규 {saved_count}개, 중복 생략 {skipped_count}개")