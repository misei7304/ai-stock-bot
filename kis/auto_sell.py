import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from kis.balance import get_balance
from kis.price import get_stock_price
from kis.safe_order import safe_sell_market_order
from storage.kis_trade_database import save_kis_trade


load_dotenv()


AUTO_SELL_ENABLED = (
    os.getenv("AUTO_SELL_ENABLED", "false")
    .strip()
    .lower()
    == "true"
)

KIS_SELL_DRY_RUN = (
    os.getenv("KIS_SELL_DRY_RUN", "true")
    .strip()
    .lower()
    == "true"
)

KIS_STOP_LOSS_RATE = float(
    os.getenv("KIS_STOP_LOSS_RATE", "0.05")
)

KIS_TAKE_PROFIT_RATE = float(
    os.getenv("KIS_TAKE_PROFIT_RATE", "0.10")
)

SELL_LOG_PATH = Path("logs/kis_sell_log.jsonl")


def parse_int(value):
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def parse_float(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def save_sell_log(data):
    SELL_LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    row = {
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        **data,
    }

    with open(
        SELL_LOG_PATH,
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                row,
                ensure_ascii=False,
            )
            + "\n"
        )

def save_sell_trade_to_database(result):
    order_result = result.get("order_result", {})
    submitted_order = order_result.get("order", {})

    return save_kis_trade(
        trade_type="sell",
        stock_code=result.get("stock_code"),
        stock_name=result.get("stock_name"),
        quantity=int(result.get("quantity") or 0),
        average_buy_price=result.get(
            "average_price"
        ),
        order_price=submitted_order.get(
            "price"
        ),
        current_price=result.get(
            "current_price"
        ),
        return_rate=result.get(
            "return_rate"
        ),
        estimated_amount=(
            float(result.get("current_price") or 0)
            * int(result.get("quantity") or 0)
        ),
        status=result.get("status"),
        reason=result.get("reason"),
        order_number=submitted_order.get(
            "order_number"
        ),
        order_time=submitted_order.get(
            "order_time"
        ),
        message=result.get("message"),
        error=result.get("error"),
    )

def get_holdings():
    result = get_balance()
    holdings = []

    for stock in result.get("output1", []):
        stock_code = str(
            stock.get("pdno") or ""
        ).strip()

        quantity = parse_int(
            stock.get("hldg_qty")
        )

        if not stock_code or quantity <= 0:
            continue

        average_price = parse_float(
            stock.get("pchs_avg_pric")
        )

        holdings.append({
            "stock_code": stock_code,
            "stock_name": stock.get(
                "prdt_name"
            ),
            "quantity": quantity,
            "average_price": average_price,
            "balance_current_price": parse_float(
                stock.get("prpr")
            ),
            "evaluation_profit_loss": parse_float(
                stock.get("evlu_pfls_amt")
            ),
        })

    return holdings


def calculate_sell_signal(
    average_price,
    current_price,
):
    if average_price <= 0:
        raise ValueError(
            "평균 매수가가 0원 이하입니다."
        )

    if current_price <= 0:
        raise ValueError(
            "현재가가 0원 이하입니다."
        )

    return_rate = (
        current_price - average_price
    ) / average_price

    stop_loss_price = average_price * (
        1 - KIS_STOP_LOSS_RATE
    )

    take_profit_price = average_price * (
        1 + KIS_TAKE_PROFIT_RATE
    )

    should_sell = False
    reason = "보유 유지"

    if current_price <= stop_loss_price:
        should_sell = True
        reason = (
            f"손절 기준 {KIS_STOP_LOSS_RATE:.2%} 도달"
        )

    elif current_price >= take_profit_price:
        should_sell = True
        reason = (
            f"목표수익 기준 "
            f"{KIS_TAKE_PROFIT_RATE:.2%} 도달"
        )

    return {
        "average_price": average_price,
        "current_price": current_price,
        "return_rate": return_rate,
        "stop_loss_price": stop_loss_price,
        "take_profit_price": take_profit_price,
        "should_sell": should_sell,
        "reason": reason,
    }


def evaluate_holding(holding):
    stock_code = holding["stock_code"]

    stock_price = get_stock_price(stock_code)
    current_price = stock_price["price"]

    signal = calculate_sell_signal(
        average_price=holding["average_price"],
        current_price=current_price,
    )

    return {
        **holding,
        **signal,
    }


def execute_auto_sell(holding_result):
    if not holding_result["should_sell"]:
        return {
            "status": "hold",
            **holding_result,
            "message": "현재 매도 조건에 해당하지 않습니다.",
        }

    request_data = {
        "stock_code": holding_result[
            "stock_code"
        ],
        "stock_name": holding_result[
            "stock_name"
        ],
        "quantity": holding_result[
            "quantity"
        ],
        "average_price": holding_result[
            "average_price"
        ],
        "current_price": holding_result[
            "current_price"
        ],
        "return_rate": holding_result[
            "return_rate"
        ],
        "reason": holding_result[
            "reason"
        ],
    }

    if not AUTO_SELL_ENABLED:
        result = {
            "status": "blocked",
            **request_data,
            "message": (
                "자동매도 기능이 비활성화되어 "
                "매도 주문을 보내지 않았습니다."
            ),
        }

        save_sell_log(result)
        save_sell_trade_to_database(result)
        return result

    if KIS_SELL_DRY_RUN:
        result = {
            "status": "dry_run",
            **request_data,
            "message": (
                "자동매도 조건은 충족했지만 "
                "드라이런이므로 실제 주문은 "
                "전송하지 않았습니다."
            ),
        }

        save_sell_log(result)
        save_sell_trade_to_database(result)
        return result

    try:
        order_result = safe_sell_market_order(
            stock_code=request_data[
                "stock_code"
            ],
            quantity=request_data[
                "quantity"
            ],
        )

        result = {
            "status": "submitted",
            **request_data,
            "order_result": order_result,
        }

        save_sell_log(result)
        save_sell_trade_to_database(result)
        return result

    except Exception:
        raise


def monitor_and_sell_holdings():
    holdings = get_holdings()
    results = []

    if not holdings:
        return results

    for index, holding in enumerate(holdings):
        if index > 0:
            import time
            time.sleep(1.0)

        try:
            holding_result = evaluate_holding(
                holding
            )

            sell_result = execute_auto_sell(
                holding_result
            )

            results.append(sell_result)

        except Exception as error:
            failed_result = {
                "status": "failed",
                "stock_code": holding.get(
                    "stock_code"
                ),
                "stock_name": holding.get(
                    "stock_name"
                ),
                "quantity": holding.get(
                    "quantity"
                ),
                "error": str(error),
            }

            save_sell_log(failed_result)
            save_sell_trade_to_database(failed_result)
            results.append(failed_result)

    return results


def print_auto_sell_results(results):
    print("\n" + "#" * 80)
    print("KIS 자동매도 점검 결과")
    print("#" * 80)

    if not results:
        print("보유 종목이 없습니다.")
        return

    for result in results:
        print("-" * 80)

        print(
            f"{result.get('stock_name')} "
            f"({result.get('stock_code')})"
        )

        print(
            f"상태: {result.get('status')}"
        )

        if result.get("status") == "failed":
            print(
                f"오류: {result.get('error')}"
            )
            continue

        print(
            f"보유수량: "
            f"{result.get('quantity', 0)}주"
        )

        print(
            f"평균매수가: "
            f"{result.get('average_price', 0):,.0f}원"
        )

        print(
            f"현재가: "
            f"{result.get('current_price', 0):,.0f}원"
        )

        print(
            f"수익률: "
            f"{result.get('return_rate', 0):+.2%}"
        )

        print(
            f"손절가: "
            f"{result.get('stop_loss_price', 0):,.0f}원"
        )

        print(
            f"목표가: "
            f"{result.get('take_profit_price', 0):,.0f}원"
        )

        print(
            f"판단 이유: "
            f"{result.get('reason')}"
        )

        if result.get("message"):
            print(result["message"])


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("KIS 자동매도 실행기")
    print("#" * 80)

    print(
        f"자동매도 활성화: {AUTO_SELL_ENABLED}"
    )
    print(
        f"매도 드라이런: {KIS_SELL_DRY_RUN}"
    )
    print(
        f"손절 기준: {KIS_STOP_LOSS_RATE:.2%}"
    )
    print(
        f"목표수익 기준: "
        f"{KIS_TAKE_PROFIT_RATE:.2%}"
    )

    results = monitor_and_sell_holdings()
    print_auto_sell_results(results)