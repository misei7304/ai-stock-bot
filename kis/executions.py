import time
from datetime import datetime

import requests

from kis.auth import get_access_token
from kis_config import (
    KIS_APP_KEY,
    KIS_APP_SECRET,
    KIS_ACCOUNT_NO,
    KIS_ACCOUNT_PRODUCT_CODE,
    KIS_BASE_URL,
)


def get_order_executions(
    start_date=None,
    end_date=None,
    stock_code="",
    execution_filter="00",
    max_retries=3,
    retry_delay=1.0,
):
    """
    국내주식 일별 주문·체결 내역 조회

    execution_filter
    - "00": 전체
    - "01": 체결
    - "02": 미체결
    """

    access_token = get_access_token()

    today = datetime.now().strftime("%Y%m%d")

    if start_date is None:
        start_date = today

    if end_date is None:
        end_date = today

    url = (
        f"{KIS_BASE_URL}"
        "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
    )

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "VTTC0081R",
        "custtype": "P",
    }

    params = {
        "CANO": KIS_ACCOUNT_NO,
        "ACNT_PRDT_CD": KIS_ACCOUNT_PRODUCT_CODE,
        "INQR_STRT_DT": start_date,
        "INQR_END_DT": end_date,
        "SLL_BUY_DVSN_CD": "00",
        "INQR_DVSN": "00",
        "PDNO": stock_code,
        "CCLD_DVSN": execution_filter,
        "ORD_GNO_BRNO": "",
        "ODNO": "",
        "INQR_DVSN_3": "00",
        "INQR_DVSN_1": "",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": "",
    }

    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=15,
            )

            data = response.json()

            if data.get("msg_cd") == "EGW00201":
                if attempt < max_retries:
                    wait_seconds = retry_delay * attempt

                    print(
                        "KIS 주문·체결 조회 호출 제한 발생: "
                        f"{wait_seconds:.1f}초 후 재시도 "
                        f"({attempt}/{max_retries})"
                    )

                    time.sleep(wait_seconds)
                    continue

                raise RuntimeError(
                    "KIS 주문·체결 조회 호출 제한이 계속 발생했습니다.\n"
                    f"종목코드: {stock_code or '전체'}\n"
                    f"메시지: {data.get('msg1')}"
                )

            response.raise_for_status()

            if data.get("rt_cd") != "0":
                raise RuntimeError(
                    "KIS 주문·체결 조회 응답 오류\n"
                    f"메시지 코드: {data.get('msg_cd')}\n"
                    f"메시지: {data.get('msg1')}\n"
                    f"전체 응답: {data}"
                )

            rows = []

            for item in data.get("output1", []):
                order_quantity = int(
                    item.get("ord_qty") or 0
                )
                executed_quantity = int(
                    item.get("tot_ccld_qty") or 0
                )
                remaining_quantity = int(
                    item.get("rmn_qty") or 0
                )

                rows.append({
                    "order_date": item.get("ord_dt"),
                    "order_time": item.get("ord_tmd"),
                    "order_number": item.get("odno"),
                    "stock_code": item.get("pdno"),
                    "stock_name": item.get("prdt_name"),
                    "side": item.get(
                        "sll_buy_dvsn_cd_name"
                    ),
                    "order_type": item.get(
                        "ord_dvsn_name"
                    ),
                    "order_quantity": order_quantity,
                    "order_price": int(
                        item.get("ord_unpr") or 0
                    ),
                    "executed_quantity": (
                        executed_quantity
                    ),
                    "executed_price": int(
                        float(item.get("avg_prvs") or 0)
                    ),
                    "remaining_quantity": (
                        remaining_quantity
                    ),
                    "is_fully_executed": (
                        order_quantity > 0
                        and remaining_quantity == 0
                        and executed_quantity
                        == order_quantity
                    ),
                })

            return rows

        except requests.RequestException as error:
            last_error = error

            if attempt < max_retries:
                wait_seconds = retry_delay * attempt
                time.sleep(wait_seconds)
                continue

            response_text = ""

            if getattr(error, "response", None) is not None:
                response_text = error.response.text

            raise RuntimeError(
                "KIS 주문·체결 내역 조회 실패\n"
                f"오류: {error}\n"
                f"응답: {response_text}"
            ) from error

        except ValueError as error:
            last_error = error

            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
                continue

            raise RuntimeError(
                "KIS 주문·체결 응답을 JSON으로 "
                "해석하지 못했습니다."
            ) from error

    raise RuntimeError(
        "KIS 주문·체결 조회에 실패했습니다.\n"
        f"마지막 오류: {last_error}"
    )


def print_order_executions(rows):
    print("\n" + "#" * 80)
    print("KIS 주문·체결 내역")
    print("#" * 80)

    if not rows:
        print("조회된 주문 내역이 없습니다.")
        return

    for row in rows:
        print("-" * 80)
        print(
            f"{row['order_date']} {row['order_time']} | "
            f"{row['stock_name']} ({row['stock_code']})"
        )
        print(
            f"주문번호: {row['order_number']} | "
            f"구분: {row['side']} | "
            f"주문유형: {row['order_type']}"
        )
        print(
            f"주문수량: {row['order_quantity']}주 | "
            f"주문가격: {row['order_price']:,}원"
        )
        print(
            f"체결수량: {row['executed_quantity']}주 | "
            f"평균체결가: {row['executed_price']:,}원 | "
            f"미체결수량: {row['remaining_quantity']}주"
        )
        print(
            "체결상태: "
            + (
                "완전체결"
                if row["is_fully_executed"]
                else "미체결 또는 부분체결"
            )
        )


if __name__ == "__main__":
    executions = get_order_executions()
    print_order_executions(executions)