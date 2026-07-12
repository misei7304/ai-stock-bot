import sqlite3


DB_NAME = "stock_bot.db"


AI_PERFORMANCE_COLUMNS = [
    ("current_close", "REAL"),
    ("current_return", "REAL"),
    ("return_1d", "REAL"),
    ("return_5d", "REAL"),
    ("return_20d", "REAL"),
]


def ensure_ai_performance_columns():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for column_name, column_type in AI_PERFORMANCE_COLUMNS:
        try:
            cursor.execute(
                f"""
                ALTER TABLE ai_observations
                ADD COLUMN {column_name} {column_type}
                """
            )
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


def get_ai_observations():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, ticker, ai_date, ai_close
        FROM ai_observations
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    observations = []

    for row in rows:
        observations.append(
            {
                "id": row[0],
                "ticker": row[1],
                "ai_date": row[2],
                "ai_close": row[3],
            }
        )

    return observations


def update_ai_observation_returns(
    observation_id,
    current_close,
    current_return,
    return_1d,
    return_5d,
    return_20d,
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE ai_observations
        SET
            current_close = ?,
            current_return = ?,
            return_1d = ?,
            return_5d = ?,
            return_20d = ?
        WHERE id = ?
        """,
        (
            current_close,
            current_return,
            return_1d,
            return_5d,
            return_20d,
            observation_id,
        ),
    )

    conn.commit()
    conn.close()