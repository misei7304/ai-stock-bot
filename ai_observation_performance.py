import sqlite3
import yfinance as yf
import pandas as pd


DB_NAME = "stock_bot.db"


def update_ai_observation_performance():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        ALTER TABLE ai_observations
        ADD COLUMN current_close REAL
    """) if False else None

    columns_to_add = [
        ("current_close", "REAL"),
        ("current_return", "REAL"),
        ("return_1d", "REAL"),
        ("return_5d", "REAL"),
        ("return_20d", "REAL"),
    ]

    for column_name, column_type in columns_to_add:
        try:
            cursor.execute(f"""
                ALTER TABLE ai_observations
                ADD COLUMN {column_name} {column_type}
            """)
        except sqlite3.OperationalError:
            pass

    cursor.execute("""
        SELECT id, ticker, ai_date, ai_close
        FROM ai_observations
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    for row in rows:
        obs_id, ticker, ai_date, ai_close = row

        df = yf.download(ticker, period="2mo", progress=False)

        if df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna()

        if ai_date not in df.index.strftime("%Y-%m-%d").tolist():
            continue

        date_list = list(df.index.strftime("%Y-%m-%d"))
        base_index = date_list.index(ai_date)

        current_close = float(df["Close"].iloc[-1])
        current_return = (current_close / ai_close - 1) * 100

        return_1d = None
        return_5d = None
        return_20d = None

        if base_index + 1 < len(df):
            close_1d = float(df["Close"].iloc[base_index + 1])
            return_1d = (close_1d / ai_close - 1) * 100

        if base_index + 5 < len(df):
            close_5d = float(df["Close"].iloc[base_index + 5])
            return_5d = (close_5d / ai_close - 1) * 100

        if base_index + 20 < len(df):
            close_20d = float(df["Close"].iloc[base_index + 20])
            return_20d = (close_20d / ai_close - 1) * 100

        cursor.execute("""
            UPDATE ai_observations
            SET
                current_close = ?,
                current_return = ?,
                return_1d = ?,
                return_5d = ?,
                return_20d = ?
            WHERE id = ?
        """, (
            current_close,
            current_return,
            return_1d,
            return_5d,
            return_20d,
            obs_id
        ))

        print(
            f"{ai_date} | {ticker} | "
            f"AI추천가 {ai_close:,.0f}원 | "
            f"현재가 {current_close:,.0f}원 | "
            f"현재수익률 {current_return:.2f}%"
        )

    conn.commit()
    conn.close()

    print("AI 후보 수익률 업데이트 완료")