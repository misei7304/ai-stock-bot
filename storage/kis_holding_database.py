import sqlite3
from datetime import datetime
from pathlib import Path


DATABASE_PATH = Path("stock_bot.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_kis_holding_table():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS kis_holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL UNIQUE,
                stock_name TEXT,
                quantity INTEGER NOT NULL,
                average_buy_price REAL,
                current_price REAL,
                evaluation_amount REAL,
                evaluation_profit_loss REAL,
                return_rate REAL,
                synchronized_at TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def upsert_kis_holding(
    stock_code,
    quantity,
    stock_name=None,
    average_buy_price=None,
    current_price=None,
    evaluation_amount=None,
    evaluation_profit_loss=None,
    return_rate=None,
):
    initialize_kis_holding_table()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO kis_holdings (
                stock_code,
                stock_name,
                quantity,
                average_buy_price,
                current_price,
                evaluation_amount,
                evaluation_profit_loss,
                return_rate,
                synchronized_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(stock_code)
            DO UPDATE SET
                stock_name = excluded.stock_name,
                quantity = excluded.quantity,
                average_buy_price =
                    excluded.average_buy_price,
                current_price =
                    excluded.current_price,
                evaluation_amount =
                    excluded.evaluation_amount,
                evaluation_profit_loss =
                    excluded.evaluation_profit_loss,
                return_rate =
                    excluded.return_rate,
                synchronized_at =
                    excluded.synchronized_at
            """,
            (
                stock_code,
                stock_name,
                quantity,
                average_buy_price,
                current_price,
                evaluation_amount,
                evaluation_profit_loss,
                return_rate,
                datetime.now().isoformat(
                    timespec="seconds"
                ),
            ),
        )

        connection.commit()

    finally:
        connection.close()


def delete_missing_kis_holdings(
    current_stock_codes,
):
    initialize_kis_holding_table()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        if not current_stock_codes:
            cursor.execute(
                "DELETE FROM kis_holdings"
            )

        else:
            placeholders = ", ".join(
                "?"
                for _ in current_stock_codes
            )

            cursor.execute(
                f"""
                DELETE FROM kis_holdings
                WHERE stock_code NOT IN (
                    {placeholders}
                )
                """,
                tuple(current_stock_codes),
            )

        connection.commit()

    finally:
        connection.close()


def get_kis_holdings():
    initialize_kis_holding_table()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM kis_holdings
            ORDER BY evaluation_amount DESC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()


def print_kis_holdings():
    holdings = get_kis_holdings()

    print("\n" + "#" * 80)
    print("KIS DB 보유 종목")
    print("#" * 80)

    if not holdings:
        print("DB에 저장된 보유 종목이 없습니다.")
        return

    for holding in holdings:
        print("-" * 80)

        print(
            f"{holding.get('stock_name') or ''} "
            f"({holding['stock_code']})"
        )

        print(
            f"보유수량: "
            f"{holding['quantity']}주"
        )

        print(
            f"평균매수가: "
            f"{holding.get('average_buy_price') or 0:,.0f}원"
        )

        print(
            f"현재가: "
            f"{holding.get('current_price') or 0:,.0f}원"
        )

        print(
            f"평가금액: "
            f"{holding.get('evaluation_amount') or 0:,.0f}원"
        )

        print(
            f"평가손익: "
            f"{holding.get('evaluation_profit_loss') or 0:+,.0f}원"
        )

        print(
            f"수익률: "
            f"{holding.get('return_rate') or 0:+.2%}"
        )

        print(
            f"동기화시각: "
            f"{holding['synchronized_at']}"
        )


if __name__ == "__main__":
    initialize_kis_holding_table()
    print_kis_holdings()