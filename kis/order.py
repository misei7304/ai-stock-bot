import requests

from kis.auth import get_access_token
from kis_config import (
    KIS_APP_KEY,
    KIS_APP_SECRET,
    KIS_ACCOUNT_NO,
    KIS_ACCOUNT_PRODUCT_CODE,
    KIS_BASE_URL,
)


ORDER_URL = (
    f"{KIS_BASE_URL}"
    "/uapi/domestic-stock/v1/trading/order-cash"
)


def validate_order(stock_code, quantity, price):
    if not stock_code:
        raise ValueError("종목코드가 없습니다.")

    stock_code = str(stock_code).strip()

    if not stock_code.isdigit() or len(stock_code) != 6:
        raise ValueError(
            "종목코드는 숫자 6자리여야 합니다. "
            "예: 005930"
        )

    if not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("주문 수량은 1 이상의 정수여야 합니다.")

    if not isinstance(price, int) or price < 0:
        raise ValueError("주문 가격은 0 이상의 정수여야 합니다.")

    return stock_code


def send_order(
    stock_code,
    quantity,
    price=0,
    order_type="01",
    transaction_id="VTTC0802U",
):
    stock_code = validate_order(
        stock_code=stock_code,
        quantity=quantity,
        price=price,
    )

    access_token = get_access_token()

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": transaction_id,
        "custtype": "P",
    }

    body = {
        "CANO": KIS_ACCOUNT_NO,
        "ACNT_PRDT_CD": KIS_ACCOUNT_PRODUCT_CODE,
        "PDNO": stock_code,
        "ORD_DVSN": order_type,
        "ORD_QTY": str(quantity),
        "ORD_UNPR": str(price),
    }

    try:
        response = requests.post(
            ORDER_URL,
            headers=headers,
            json=body,
            timeout=15,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        response_text = ""

        if getattr(error, "response", None) is not None:
            response_text = error.response.text

        raise RuntimeError(
            "KIS 주문 요청 실패\n"
            f"종목코드: {stock_code}\n"
            f"수량: {quantity}\n"
            f"가격: {price}\n"
            f"오류: {error}\n"
            f"응답: {response_text}"
        ) from error

    data = response.json()

    if data.get("rt_cd") != "0":
        raise RuntimeError(
            "KIS 주문 응답 오류\n"
            f"종목코드: {stock_code}\n"
            f"메시지 코드: {data.get('msg_cd')}\n"
            f"메시지: {data.get('msg1')}\n"
            f"전체 응답: {data}"
        )

    output = data.get("output", {})

    return {
        "stock_code": stock_code,
        "quantity": quantity,
        "price": price,
        "order_type": order_type,
        "order_number": output.get("ODNO"),
        "order_time": output.get("ORD_TMD"),
        "message": data.get("msg1"),
        "raw_data": data,
    }


def buy_market_order(stock_code, quantity):
    return send_order(
        stock_code=stock_code,
        quantity=quantity,
        price=0,
        order_type="01",
        transaction_id="VTTC0802U",
    )


def buy_limit_order(stock_code, quantity, price):
    return send_order(
        stock_code=stock_code,
        quantity=quantity,
        price=price,
        order_type="00",
        transaction_id="VTTC0802U",
    )


def sell_market_order(stock_code, quantity):
    return send_order(
        stock_code=stock_code,
        quantity=quantity,
        price=0,
        order_type="01",
        transaction_id="VTTC0801U",
    )


def sell_limit_order(stock_code, quantity, price):
    return send_order(
        stock_code=stock_code,
        quantity=quantity,
        price=price,
        order_type="00",
        transaction_id="VTTC0801U",
    )


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("KIS 모의투자 주문 테스트")
    print("#" * 80)

    print("안전상 기본 실행에서는 실제 주문을 보내지 않습니다.")
    print(
        "buy_market_order(), buy_limit_order(), "
        "sell_market_order(), sell_limit_order()를 직접 호출하세요."
    )