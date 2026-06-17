import sqlite3


DATABASE_NAME = "stock_bot.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recommendation_date TEXT,
            company_name TEXT,
            ticker TEXT,
            recommended_price REAL,
            final_score REAL,
            current_score REAL,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            macd_histogram REAL,
            bollinger_upper REAL,
            bollinger_middle REAL,
            bollinger_lower REAL,
            bollinger_score REAL,
            atr REAL,
            atr_percent REAL,
            atr_score REAL,
            win_rate REAL,
            average_return REAL,
            final_money REAL,
            quantity INTEGER,
            investment_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendation_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recommendation_id INTEGER,
            ticker TEXT,
            company_name TEXT,
            recommendation_date TEXT,
            recommended_price REAL,
            current_price REAL,
            current_return REAL,
            return_1d REAL,
            return_5d REAL,
            return_20d REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_recommendation_to_database(stock):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM recommendations
        WHERE recommendation_date = DATE('now', 'localtime')
        AND ticker = ?
    """, (
        stock["ticker"],
    ))

    existing_count = cursor.fetchone()[0]

    if existing_count > 0:
        connection.close()
        print("이미 오늘 DB 추천 기록이 있습니다. DB 저장 생략")
        return

    position = stock["position"]

    cursor.execute("""
        INSERT INTO recommendations (
            recommendation_date,
            company_name,
            ticker,
            recommended_price,
            final_score,
            current_score,
            rsi,
            macd,
            macd_signal,
            macd_histogram,
            bollinger_upper,
            bollinger_middle,
            bollinger_lower,
            bollinger_score,
            atr,
            atr_percent,
            atr_score,
            win_rate,
            average_return,
            final_money,
            quantity,
            investment_amount
        )
        VALUES (
            DATE('now', 'localtime'),
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        stock["company_name"],
        stock["ticker"],
        stock["current_price"],
        stock["final_score"],
        stock["total_score"],
        stock["rsi"],
        stock["macd"],
        stock["macd_signal"],
        stock["macd_histogram"],
        stock["bollinger_upper"],
        stock["bollinger_middle"],
        stock["bollinger_lower"],
        stock["bollinger_score"],
        stock["atr"],
        stock["atr_percent"],
        stock["atr_score"],
        stock["win_rate"],
        stock["average_return"],
        stock["final_money"],
        position["quantity"],
        position["investment_amount"],
    ))

    connection.commit()
    connection.close()

    print("DB 추천 기록 저장 완료")