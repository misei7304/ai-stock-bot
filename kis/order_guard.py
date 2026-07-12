import time
from kis.balance import get_balance
from kis.executions import get_order_executions
from kis.price import get_stock_price


def get_holding_quantity(stock_code):
    result = get_balance()

    for stock in result.get("output1", []):
        product_code = str(stock.get("pdno", "")).strip()

        if product_code == stock_code:
            return int(stock.get("hldg_qty") or 0)

    return 0


def has_pending_buy_order(stock_code):
    executions = get_order_executions(
        stock_code=stock_code,
        execution_filter="02",
    )

    for order in executions:
        side = str(order.get("side") or "")

        if "매수" in side and order["remaining_quantity"] > 0:
            return True

    return False


def validate_buy_order(
    stock_code,
    quantity,
    max_order_amount,
):
    if not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("매수 수량은 1주 이상의 정수여야 합니다.")

    if max_order_amount <= 0:
        raise ValueError("최대 주문금액은 0원보다 커야 합니다.")

    holding_quantity = get_holding_quantity(stock_code)

    if holding_quantity > 0:
        raise RuntimeError(
            "이미 보유 중인 종목은 추가 매수할 수 없습니다.\n"
            f"종목코드: {stock_code}\n"
            f"보유수량: {holding_quantity}주"
        )
    
    time.sleep(1.0)

    if has_pending_buy_order(stock_code):
        raise RuntimeError(
            f"{stock_code} 종목에 미체결 매수 주문이 이미 있습니다."
        )
    
    time.sleep(1.0)

    stock = get_stock_price(stock_code)
    current_price = stock["price"]
    estimated_amount = current_price * quantity

    if estimated_amount > max_order_amount:
        raise RuntimeError(
            "주문 가능 금액을 초과했습니다.\n"
            f"종목코드: {stock_code}\n"
            f"현재가: {current_price:,}원\n"
            f"주문수량: {quantity}주\n"
            f"예상 주문금액: {estimated_amount:,}원\n"
            f"최대 주문금액: {max_order_amount:,}원"
        )

    return {
        "stock_code": stock_code,
        "quantity": quantity,
        "current_price": current_price,
        "estimated_amount": estimated_amount,
        "holding_quantity": holding_quantity,
    }


def validate_sell_order(stock_code, quantity):
    if quantity <= 0:
        raise ValueError("매도 수량은 1주 이상이어야 합니다.")

    holding_quantity = get_holding_quantity(stock_code)

    if holding_quantity < quantity:
        raise RuntimeError(
            "보유 수량보다 많은 수량을 매도할 수 없습니다.\n"
            f"종목코드: {stock_code}\n"
            f"보유수량: {holding_quantity}주\n"
            f"매도요청수량: {quantity}주"
        )

    return {
        "stock_code": stock_code,
        "quantity": quantity,
        "holding_quantity": holding_quantity,
    }


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("KIS 주문 안전장치")
    print("#" * 80)

    print(f"삼성전자 보유수량: {get_holding_quantity('005930')}주")
    print(
        "삼성전자 미체결 매수 주문 존재 여부: "
        f"{has_pending_buy_order('005930')}"
    )