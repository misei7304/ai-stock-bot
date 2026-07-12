import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from kis.safe_order import safe_buy_market_order
from storage.kis_trade_database import (
    count_kis_trades_today,
    has_kis_trade_today,
    save_kis_trade,
)


load_dotenv()


AUTO_TRADING_ENABLED = (
    os.getenv("AUTO_TRADING_ENABLED", "false")
    .strip()
    .lower()
    == "true"
)

KIS_DRY_RUN = (
    os.getenv("KIS_DRY_RUN", "true")
    .strip()
    .lower()
    == "true"
)

KIS_MAX_ORDER_AMOUNT = int(
    os.getenv("KIS_MAX_ORDER_AMOUNT", "300000")
)

KIS_MAX_DAILY_ORDERS = int(
    os.getenv("KIS_MAX_DAILY_ORDERS", "1")
)

KIS_MIN_AI_PROBABILITY = float(
    os.getenv("KIS_MIN_AI_PROBABILITY", "0.78")
)

ORDER_LOG_PATH = Path("logs/kis_order_log.jsonl")


def validate_auto_trade_input(
    stock_code,
    quantity,
    ai_probability,
    market_is_bull,
    risk_allowed,
):
    stock_code = str(stock_code).strip()

    if not stock_code.isdigit() or len(stock_code) != 6:
        raise ValueError(
            "종목코드는 숫자 6자리여야 합니다."
        )

    if not isinstance(quantity, int) or quantity <= 0:
        raise ValueError(
            "주문 수량은 1주 이상의 정수여야 합니다."
        )

    if not 0 <= ai_probability <= 1:
        raise ValueError(
            "AI 확률은 0과 1 사이여야 합니다."
        )

    if not market_is_bull:
        raise RuntimeError(
            "시장 상태가 약세장이므로 자동매수를 차단합니다."
        )

    if not risk_allowed:
        raise RuntimeError(
            "실전 리스크 가드가 매수를 허용하지 않았습니다."
        )

    if ai_probability < KIS_MIN_AI_PROBABILITY:
        raise RuntimeError(
            "AI 상승확률이 자동매수 기준보다 낮습니다.\n"
            f"AI 상승확률: {ai_probability:.2%}\n"
            f"최소 기준: {KIS_MIN_AI_PROBABILITY:.2%}"
        )

    return stock_code


def load_today_order_count():
    return count_kis_trades_today(
        trade_type="buy",
        statuses=(
            "dry_run",
            "submitted",
        ),
    )


def save_order_log(data):
    ORDER_LOG_PATH.parent.mkdir(
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
        ORDER_LOG_PATH,
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

def save_buy_trade_to_database(result):
    order_result = result.get("order_result", {})
    validation = order_result.get("validation", {})
    submitted_order = order_result.get("order", {})

    current_price = result.get("current_price")

    if current_price is None:
        current_price = validation.get(
            "current_price"
        )

    estimated_amount = result.get(
        "estimated_amount"
    )

    if estimated_amount is None:
        estimated_amount = validation.get(
            "estimated_amount"
        )

    return save_kis_trade(
        trade_type="buy",
        stock_code=result.get("stock_code"),
        stock_name=result.get("stock_name"),
        quantity=int(
            result.get("quantity") or 0
        ),
        average_buy_price=None,
        order_price=submitted_order.get(
            "price"
        ),
        current_price=current_price,
        return_rate=None,
        estimated_amount=estimated_amount,
        status=result.get("status"),
        reason=(
            f"AI 상승확률 "
            f"{float(result.get('ai_probability') or 0):.2%}"
        ),
        order_number=submitted_order.get(
            "order_number"
        ),
        order_time=submitted_order.get(
            "order_time"
        ),
        message=result.get("message"),
        error=result.get("error"),
    )


def execute_auto_buy(
    stock_code,
    quantity,
    ai_probability,
    market_is_bull,
    risk_allowed,
    current_price=None,
    estimated_amount=None,
    stock_name=None,
):
    stock_code = validate_auto_trade_input(
        stock_code=stock_code,
        quantity=quantity,
        ai_probability=ai_probability,
        market_is_bull=market_is_bull,
        risk_allowed=risk_allowed,
    )

    if not AUTO_TRADING_ENABLED:
        raise RuntimeError(
            "자동주문 기능이 비활성화되어 있습니다.\n"
            "AUTO_TRADING_ENABLED=true로 설정해야 합니다."
        )
    
    if has_kis_trade_today(
        trade_type="buy",
        stock_code=stock_code,
        statuses=(
            "dry_run",
            "submitted",
        ),
    ):
        raise RuntimeError(
            "오늘 이미 동일 종목의 자동매수 기록이 있습니다.\n"
            f"종목코드: {stock_code}\n"
            "중복 자동매수를 차단했습니다."
        )

    today_order_count = load_today_order_count()

    if today_order_count >= KIS_MAX_DAILY_ORDERS:
        raise RuntimeError(
            "일일 최대 주문 횟수를 초과했습니다.\n"
            f"오늘 주문 횟수: {today_order_count}회\n"
            f"최대 주문 횟수: "
            f"{KIS_MAX_DAILY_ORDERS}회"
        )

    request_data = {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "quantity": quantity,
        "ai_probability": ai_probability,
        "market_is_bull": market_is_bull,
        "risk_allowed": risk_allowed,
        "current_price": current_price,
        "estimated_amount": estimated_amount,
        "max_order_amount": (
            KIS_MAX_ORDER_AMOUNT
        ),
    }

    if KIS_DRY_RUN:
        result = {
            "status": "dry_run",
            **request_data,
            "message": (
                "드라이런 상태이므로 실제 주문은 "
                "전송하지 않았습니다."
            ),
        }

        save_order_log(result)
        save_buy_trade_to_database(result)

        return result

    try:
        order_result = safe_buy_market_order(
            stock_code=stock_code,
            quantity=quantity,
            max_order_amount=(
                KIS_MAX_ORDER_AMOUNT
            ),
        )

        result = {
            "status": "submitted",
            **request_data,
            "order_result": order_result,
        }

        save_order_log(result)
        save_buy_trade_to_database(result)

        return result

    except Exception as error:
        failed_result = {
            "status": "failed",
            **request_data,
            "error": str(error),
        }

        save_order_log(failed_result)
        save_buy_trade_to_database(
            failed_result
        )

        raise


def print_auto_trade_result(result):
    print("\n" + "#" * 80)
    print("KIS 자동매매 실행 결과")
    print("#" * 80)

    print(f"상태: {result['status']}")
    print(f"종목코드: {result['stock_code']}")
    print(f"주문수량: {result['quantity']}주")
    print(
        "AI 상승확률: "
        f"{result['ai_probability']:.2%}"
    )
    print(
        "최대 주문금액: "
        f"{result['max_order_amount']:,}원"
    )

    if result["status"] == "dry_run":
        print(result["message"])
        return

    order = result.get("order_result", {})
    validation = order.get("validation", {})
    submitted_order = order.get("order", {})

    print(
        "검증 당시 현재가: "
        f"{validation.get('current_price', 0):,}원"
    )
    print(
        "예상 주문금액: "
        f"{validation.get('estimated_amount', 0):,}원"
    )
    print(
        "주문번호: "
        f"{submitted_order.get('order_number')}"
    )
    print(
        "주문시각: "
        f"{submitted_order.get('order_time')}"
    )


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("KIS 자동매매 실행기")
    print("#" * 80)

    print(
        f"자동주문 활성화: {AUTO_TRADING_ENABLED}"
    )
    print(f"드라이런: {KIS_DRY_RUN}")
    print(
        f"최소 AI 확률: "
        f"{KIS_MIN_AI_PROBABILITY:.2%}"
    )
    print(
        f"최대 주문금액: "
        f"{KIS_MAX_ORDER_AMOUNT:,}원"
    )
    print(
        f"일일 최대 주문수: "
        f"{KIS_MAX_DAILY_ORDERS}회"
    )

    print(
        "\n기본 실행에서는 주문을 보내지 않습니다."
    )
    print(
        "execute_auto_buy()를 호출해야 합니다."
    )