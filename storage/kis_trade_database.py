import sqlite3
from datetime import datetime
from pathlib import Path


DATABASE_PATH = Path("stock_bot.db")


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def initialize_kis_trade_tables():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS kis_trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                quantity INTEGER NOT NULL,
                average_buy_price REAL,
                order_price REAL,
                current_price REAL,
                return_rate REAL,
                estimated_amount REAL,
                status TEXT NOT NULL,
                reason TEXT,
                order_number TEXT,
                order_time TEXT,
                message TEXT,
                error TEXT
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def save_kis_trade(
    trade_type,
    stock_code,
    quantity,
    status,
    stock_name=None,
    average_buy_price=None,
    order_price=None,
    current_price=None,
    return_rate=None,
    estimated_amount=None,
    reason=None,
    order_number=None,
    order_time=None,
    message=None,
    error=None,
):
    initialize_kis_trade_tables()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO kis_trade_history (
                created_at,
                trade_type,
                stock_code,
                stock_name,
                quantity,
                average_buy_price,
                order_price,
                current_price,
                return_rate,
                estimated_amount,
                status,
                reason,
                order_number,
                order_time,
                message,
                error
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(
                    timespec="seconds"
                ),
                trade_type,
                stock_code,
                stock_name,
                quantity,
                average_buy_price,
                order_price,
                current_price,
                return_rate,
                estimated_amount,
                status,
                reason,
                order_number,
                order_time,
                message,
                error,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_recent_kis_trades(limit=20):
    initialize_kis_trade_tables()

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM kis_trade_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()


def print_recent_kis_trades(limit=20):
    rows = get_recent_kis_trades(limit)

    print("\n" + "#" * 80)
    print("KIS 최근 자동매매 기록")
    print("#" * 80)

    if not rows:
        print("저장된 KIS 자동매매 기록이 없습니다.")
        return

    for row in rows:
        print("-" * 80)
        print(
            f"{row['created_at']} | "
            f"{row['trade_type']} | "
            f"{row['stock_name'] or ''} "
            f"({row['stock_code']})"
        )
        print(
            f"상태: {row['status']} | "
            f"수량: {row['quantity']}주 | "
            f"주문번호: {row['order_number']}"
        )

        if row["current_price"] is not None:
            print(
                f"현재가: "
                f"{row['current_price']:,.0f}원"
            )

        if row["return_rate"] is not None:
            print(
                f"수익률: "
                f"{row['return_rate']:+.2%}"
            )

        if row["reason"]:
            print(f"이유: {row['reason']}")

        if row["message"]:
            print(f"메시지: {row['message']}")

        if row["error"]:
            print(f"오류: {row['error']}")


if __name__ == "__main__":
    initialize_kis_trade_tables()
    print_recent_kis_trades()