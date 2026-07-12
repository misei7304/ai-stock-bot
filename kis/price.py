import time

import requests

from kis.auth import get_access_token
from kis_config import (
    KIS_APP_KEY,
    KIS_APP_SECRET,
    KIS_BASE_URL,
)


def get_stock_price(
    stock_code,
    max_retries=3,
    retry_delay=1.0,
):
    access_token = get_access_token()

    url = (
        f"{KIS_BASE_URL}"
        "/uapi/domestic-stock/v1/quotations/inquire-price"
    )

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "FHKST01010100",
        "custtype": "P",
    }

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code,
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
                        "KIS 호출 제한 발생: "
                        f"{wait_seconds:.1f}초 후 재시도 "
                        f"({attempt}/{max_retries})"
                    )

                    time.sleep(wait_seconds)
                    continue

                raise RuntimeError(
                    "KIS API 호출 제한이 계속 발생했습니다.\n"
                    f"종목코드: {stock_code}\n"
                    f"메시지: {data.get('msg1')}"
                )

            response.raise_for_status()

            if data.get("rt_cd") != "0":
                raise RuntimeError(
                    "KIS 현재가 조회 응답 오류\n"
                    f"종목코드: {stock_code}\n"
                    f"메시지 코드: {data.get('msg_cd')}\n"
                    f"메시지: {data.get('msg1')}"
                )

            output = data.get("output")

            if not output:
                raise RuntimeError(
                    f"KIS 응답에 현재가 데이터가 없습니다: {data}"
                )

            return {
                "stock_code": stock_code,
                "price": int(output["stck_prpr"]),
                "change": int(output["prdy_vrss"]),
                "change_rate": float(output["prdy_ctrt"]),
                "open": int(output["stck_oprc"]),
                "high": int(output["stck_hgpr"]),
                "low": int(output["stck_lwpr"]),
                "volume": int(output["acml_vol"]),
                "trade_amount": int(output["acml_tr_pbmn"]),
            }

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
                "KIS 현재가 조회 실패\n"
                f"종목코드: {stock_code}\n"
                f"오류: {error}\n"
                f"응답: {response_text}"
            ) from error

        except ValueError as error:
            last_error = error

            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
                continue

            raise RuntimeError(
                "KIS 현재가 응답을 JSON으로 해석하지 못했습니다.\n"
                f"종목코드: {stock_code}"
            ) from error

    raise RuntimeError(
        "KIS 현재가 조회에 실패했습니다.\n"
        f"마지막 오류: {last_error}"
    )


if __name__ == "__main__":
    stock = get_stock_price("005930")

    print("\n" + "#" * 80)
    print("KIS 국내주식 현재가 조회")
    print("#" * 80)

    print(f"종목코드: {stock['stock_code']}")
    print(f"현재가: {stock['price']:,}원")
    print(f"전일 대비: {stock['change']:+,}원")
    print(f"등락률: {stock['change_rate']:+.2f}%")
    print(f"시가: {stock['open']:,}원")
    print(f"고가: {stock['high']:,}원")
    print(f"저가: {stock['low']:,}원")
    print(f"누적 거래량: {stock['volume']:,}주")
    print(f"누적 거래대금: {stock['trade_amount']:,}원")