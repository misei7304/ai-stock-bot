import requests

from kis.auth import get_access_token
from kis_config import (
    KIS_APP_KEY,
    KIS_APP_SECRET,
    KIS_ACCOUNT_NO,
    KIS_ACCOUNT_PRODUCT_CODE,
    KIS_BASE_URL,
)


def get_balance():
    access_token = get_access_token()

    url = (
        f"{KIS_BASE_URL}"
        "/uapi/domestic-stock/v1/trading/inquire-balance"
    )

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "VTTC8434R",
        "custtype": "P",
    }

    params = {
        "CANO": KIS_ACCOUNT_NO,
        "ACNT_PRDT_CD": KIS_ACCOUNT_PRODUCT_CODE,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": "",
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    if data["rt_cd"] != "0":
        raise RuntimeError(
            f"{data['msg_cd']} : {data['msg1']}"
        )

    return data


if __name__ == "__main__":

    result = get_balance()

    print("\n" + "#" * 80)
    print("계좌 잔고")
    print("#" * 80)

    stocks = result["output1"]

    if len(stocks) == 0:
        print("보유 종목 없음")
    else:
        for stock in stocks:
            print(
                f"{stock['prdt_name']} "
                f"{stock['hldg_qty']}주 "
                f"평균단가 {stock['pchs_avg_pric']}원 "
                f"현재가 {stock['prpr']}원 "
                f"평가손익 {stock['evlu_pfls_amt']}원"
            )

    summary = result["output2"][0]

    print("\n========== 계좌 요약 ==========")
    print(f"예수금 : {summary['dnca_tot_amt']}원")
    print(f"평가금액 : {summary['tot_evlu_amt']}원")
    print(f"평가손익 : {summary['evlu_pfls_smtl_amt']}원")