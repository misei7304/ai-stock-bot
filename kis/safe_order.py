from kis.order import (
    buy_limit_order,
    buy_market_order,
    sell_limit_order,
    sell_market_order,
)
from kis.order_guard import (
    validate_buy_order,
    validate_sell_order,
)


def safe_buy_market_order(
    stock_code,
    quantity,
    max_order_amount,
):
    validation = validate_buy_order(
        stock_code=stock_code,
        quantity=quantity,
        max_order_amount=max_order_amount,
    )

    order = buy_market_order(
        stock_code=stock_code,
        quantity=quantity,
    )

    return {
        "validation": validation,
        "order": order,
    }


def safe_buy_limit_order(
    stock_code,
    quantity,
    price,
    max_order_amount,
):
    if price <= 0:
        raise ValueError("지정가 주문 가격은 0원보다 커야 합니다.")

    estimated_amount = price * quantity

    if estimated_amount > max_order_amount:
        raise RuntimeError(
            "지정가 주문 금액이 최대 주문금액을 초과했습니다.\n"
            f"종목코드: {stock_code}\n"
            f"주문가격: {price:,}원\n"
            f"주문수량: {quantity}주\n"
            f"예상 주문금액: {estimated_amount:,}원\n"
            f"최대 주문금액: {max_order_amount:,}원"
        )

    validation = validate_buy_order(
        stock_code=stock_code,
        quantity=quantity,
        max_order_amount=max_order_amount,
    )

    order = buy_limit_order(
        stock_code=stock_code,
        quantity=quantity,
        price=price,
    )

    return {
        "validation": validation,
        "order": order,
    }


def safe_sell_market_order(stock_code, quantity):
    validation = validate_sell_order(
        stock_code=stock_code,
        quantity=quantity,
    )

    order = sell_market_order(
        stock_code=stock_code,
        quantity=quantity,
    )

    return {
        "validation": validation,
        "order": order,
    }


def safe_sell_limit_order(
    stock_code,
    quantity,
    price,
):
    if price <= 0:
        raise ValueError("지정가 주문 가격은 0원보다 커야 합니다.")

    validation = validate_sell_order(
        stock_code=stock_code,
        quantity=quantity,
    )

    order = sell_limit_order(
        stock_code=stock_code,
        quantity=quantity,
        price=price,
    )

    return {
        "validation": validation,
        "order": order,
    }


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("KIS 안전 주문 모듈")
    print("#" * 80)

    print("기본 실행에서는 주문을 보내지 않습니다.")
    print(
        "safe_buy_market_order(), safe_buy_limit_order(), "
        "safe_sell_market_order(), safe_sell_limit_order()를 사용하세요."
    )