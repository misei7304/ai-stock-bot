import sqlite3
import time
from datetime import datetime
from pathlib import Path

from kis.executions import get_order_executions


DATABASE_PATH = Path("stock_bot.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_pending_submitted_trades():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM kis_trade_history
            WHERE status = 'submitted'
              AND order_number IS NOT NULL
              AND order_number != ''
            ORDER BY id ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()


def determine_execution_status(execution):
    order_quantity = int(
        execution.get("order_quantity") or 0
    )

    executed_quantity = int(
        execution.get("executed_quantity") or 0
    )

    remaining_quantity = int(
        execution.get("remaining_quantity") or 0
    )

    if (
        order_quantity > 0
        and executed_quantity == order_quantity
        and remaining_quantity == 0
    ):
        return "filled"

    if (
        executed_quantity > 0
        and remaining_quantity > 0
    ):
        return "partial"

    if (
        executed_quantity == 0
        and remaining_quantity > 0
    ):
        return "unfilled"

    return "submitted"


def update_trade_execution(
    trade_id,
    status,
    executed_price=None,
    executed_quantity=None,
    remaining_quantity=None,
    message=None,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE kis_trade_history
            SET status = ?,
                order_price = COALESCE(
                    ?,
                    order_price
                ),
                executed_quantity = ?,
                remaining_quantity = ?,
                execution_updated_at = ?,
                message = COALESCE(
                    ?,
                    message
                )
            WHERE id = ?
            """,
            (
                status,
                executed_price,
                executed_quantity,
                remaining_quantity,
                datetime.now().isoformat(
                    timespec="seconds"
                ),
                message,
                trade_id,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def find_matching_execution(
    trade,
    executions,
):
    trade_order_number = str(
        trade.get("order_number") or ""
    ).strip()

    trade_stock_code = str(
        trade.get("stock_code") or ""
    ).strip()

    trade_type = str(
        trade.get("trade_type") or ""
    ).strip()

    for execution in executions:
        execution_order_number = str(
            execution.get("order_number") or ""
        ).strip()

        execution_stock_code = str(
            execution.get("stock_code") or ""
        ).strip()

        execution_side = str(
            execution.get("side") or ""
        )

        if (
            execution_order_number
            != trade_order_number
        ):
            continue

        if (
            execution_stock_code
            != trade_stock_code
        ):
            continue

        if (
            trade_type == "buy"
            and "매수" not in execution_side
        ):
            continue

        if (
            trade_type == "sell"
            and "매도" not in execution_side
        ):
            continue

        return execution

    return None


def synchronize_trade_executions():
    submitted_trades = (
        get_pending_submitted_trades()
    )

    results = []

    if not submitted_trades:
        return results

    grouped_dates = {}

    for trade in submitted_trades:
        created_at = datetime.fromisoformat(
            trade["created_at"]
        )

        date_text = created_at.strftime(
            "%Y%m%d"
        )

        grouped_dates.setdefault(
            date_text,
            [],
        ).append(trade)

    for date_index, (
        date_text,
        date_trades,
    ) in enumerate(grouped_dates.items()):

        if date_index > 0:
            time.sleep(1.0)

        executions = get_order_executions(
            start_date=date_text,
            end_date=date_text,
            execution_filter="00",
        )

        for trade in date_trades:
            execution = find_matching_execution(
                trade=trade,
                executions=executions,
            )

            if execution is None:
                results.append({
                    "trade_id": trade["id"],
                    "stock_code": trade[
                        "stock_code"
                    ],
                    "order_number": trade[
                        "order_number"
                    ],
                    "status": "not_found",
                    "message": (
                        "일치하는 주문·체결 내역을 "
                        "찾지 못했습니다."
                    ),
                })
                continue

            status = determine_execution_status(
                execution
            )

            executed_quantity = int(
                execution.get(
                    "executed_quantity"
                )
                or 0
            )

            executed_price = int(
                execution.get(
                    "executed_price"
                )
                or 0
            )

            message = (
                f"체결상태 동기화 | "
                f"체결수량 {executed_quantity}주 | "
                f"미체결수량 "
                f"{execution.get('remaining_quantity', 0)}주"
            )

            update_trade_execution(
                trade_id=trade["id"],
                status=status,
                executed_price=(
                    executed_price
                    if executed_price > 0
                    else None
                ),
                executed_quantity=(
                    executed_quantity
                ),
                remaining_quantity=int(
                    execution.get(
                        "remaining_quantity"
                    )
                    or 0
                ),
                message=message,
            )

            results.append({
                "trade_id": trade["id"],
                "stock_code": trade[
                    "stock_code"
                ],
                "stock_name": trade.get(
                    "stock_name"
                ),
                "order_number": trade[
                    "order_number"
                ],
                "trade_type": trade[
                    "trade_type"
                ],
                "status": status,
                "order_quantity": execution[
                    "order_quantity"
                ],
                "executed_quantity": (
                    executed_quantity
                ),
                "remaining_quantity": execution[
                    "remaining_quantity"
                ],
                "executed_price": (
                    executed_price
                ),
            })

    return results


def print_sync_results(results):
    print("\n" + "#" * 80)
    print("KIS 주문 체결 상태 동기화")
    print("#" * 80)

    if not results:
        print(
            "동기화할 submitted 주문이 없습니다."
        )
        return

    for result in results:
        print("-" * 80)

        print(
            f"{result.get('stock_name') or ''} "
            f"({result['stock_code']})"
        )

        print(
            f"거래유형: "
            f"{result.get('trade_type')}"
        )

        print(
            f"주문번호: "
            f"{result.get('order_number')}"
        )

        print(
            f"상태: "
            f"{result.get('status')}"
        )

        if result.get("status") == "not_found":
            print(result["message"])
            continue

        print(
            f"주문수량: "
            f"{result.get('order_quantity', 0)}주"
        )

        print(
            f"체결수량: "
            f"{result.get('executed_quantity', 0)}주"
        )

        print(
            f"미체결수량: "
            f"{result.get('remaining_quantity', 0)}주"
        )

        print(
            f"평균체결가: "
            f"{result.get('executed_price', 0):,}원"
        )


if __name__ == "__main__":
    sync_results = (
        synchronize_trade_executions()
    )

    print_sync_results(sync_results)