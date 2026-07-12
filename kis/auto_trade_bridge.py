from kis.auto_trader import (
    KIS_MAX_ORDER_AMOUNT,
    execute_auto_buy,
)
from kis.price import get_stock_price


def normalize_stock_code(ticker):
    ticker = str(ticker).strip()

    if ticker.endswith(".KS"):
        ticker = ticker[:-3]

    if ticker.endswith(".KQ"):
        ticker = ticker[:-3]

    if not ticker.isdigit() or len(ticker) != 6:
        raise ValueError(
            "KIS 주문용 종목코드는 숫자 6자리여야 합니다.\n"
            f"입력값: {ticker}"
        )

    return ticker


def calculate_order_quantity(
    stock_code,
    max_order_amount=None,
):
    if max_order_amount is None:
        max_order_amount = KIS_MAX_ORDER_AMOUNT

    if max_order_amount <= 0:
        raise ValueError(
            "최대 주문금액은 0원보다 커야 합니다."
        )

    stock = get_stock_price(stock_code)
    current_price = stock["price"]

    if current_price <= 0:
        raise RuntimeError(
            "현재가가 올바르지 않습니다.\n"
            f"종목코드: {stock_code}\n"
            f"현재가: {current_price}"
        )

    quantity = max_order_amount // current_price

    if quantity < 1:
        raise RuntimeError(
            "최대 주문금액으로 1주도 매수할 수 없습니다.\n"
            f"종목코드: {stock_code}\n"
            f"현재가: {current_price:,}원\n"
            f"최대 주문금액: {max_order_amount:,}원"
        )

    return {
        "stock_code": stock_code,
        "current_price": current_price,
        "quantity": int(quantity),
        "estimated_amount": int(
            current_price * quantity
        ),
        "max_order_amount": max_order_amount,
    }


def execute_candidate_auto_buy(
    ticker,
    ai_probability,
    market_is_bull,
    risk_allowed,
    max_order_amount=None,
):
    stock_code = normalize_stock_code(ticker)

    quantity_info = calculate_order_quantity(
        stock_code=stock_code,
        max_order_amount=max_order_amount,
    )

    result = execute_auto_buy(
        stock_code=stock_code,
        quantity=quantity_info["quantity"],
        ai_probability=float(ai_probability),
        market_is_bull=bool(market_is_bull),
        risk_allowed=bool(risk_allowed),
        current_price=quantity_info[
            "current_price"
        ],
        estimated_amount=quantity_info[
            "estimated_amount"
        ],
    )

    return {
        "candidate": {
            "ticker": ticker,
            "stock_code": stock_code,
            "ai_probability": float(
                ai_probability
            ),
        },
        "quantity_info": quantity_info,
        "auto_trade_result": result,
    }


def print_bridge_result(result):
    candidate = result["candidate"]
    quantity_info = result["quantity_info"]
    auto_trade_result = result[
        "auto_trade_result"
    ]

    print("\n" + "#" * 80)
    print("AI 후보 → KIS 자동매매 연결 결과")
    print("#" * 80)

    print(
        f"티커: {candidate['ticker']}"
    )
    print(
        f"KIS 종목코드: "
        f"{candidate['stock_code']}"
    )
    print(
        f"AI 상승확률: "
        f"{candidate['ai_probability']:.2%}"
    )
    print(
        f"현재가: "
        f"{quantity_info['current_price']:,}원"
    )
    print(
        f"계산 주문수량: "
        f"{quantity_info['quantity']}주"
    )
    print(
        f"예상 주문금액: "
        f"{quantity_info['estimated_amount']:,}원"
    )
    print(
        f"실행 상태: "
        f"{auto_trade_result['status']}"
    )

    if auto_trade_result["status"] == "dry_run":
        print(
            "드라이런이므로 실제 주문은 "
            "전송되지 않았습니다."
        )


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("AI 후보와 KIS 자동매매 연결 모듈")
    print("#" * 80)

    print(
        "기본 실행에서는 후보를 매수하지 않습니다."
    )
    print(
        "execute_candidate_auto_buy()를 "
        "호출해야 합니다."
    )