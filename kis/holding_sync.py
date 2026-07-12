from kis.balance import get_balance
from storage.kis_holding_database import (
    delete_missing_kis_holdings,
    print_kis_holdings,
    upsert_kis_holding,
)


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


def calculate_return_rate(
    average_buy_price,
    current_price,
):
    if average_buy_price <= 0:
        return 0.0

    return (
        current_price - average_buy_price
    ) / average_buy_price


def synchronize_kis_holdings():
    balance_result = get_balance()
    raw_holdings = balance_result.get(
        "output1",
        [],
    )

    synchronized_holdings = []
    current_stock_codes = []

    for raw_holding in raw_holdings:
        stock_code = str(
            raw_holding.get("pdno") or ""
        ).strip()

        quantity = parse_int(
            raw_holding.get("hldg_qty")
        )

        if not stock_code or quantity <= 0:
            continue

        stock_name = raw_holding.get(
            "prdt_name"
        )

        average_buy_price = parse_float(
            raw_holding.get("pchs_avg_pric")
        )

        current_price = parse_float(
            raw_holding.get("prpr")
        )

        evaluation_amount = parse_float(
            raw_holding.get("evlu_amt")
        )

        if evaluation_amount <= 0:
            evaluation_amount = (
                current_price * quantity
            )

        evaluation_profit_loss = parse_float(
            raw_holding.get("evlu_pfls_amt")
        )

        return_rate = parse_float(
            raw_holding.get("evlu_pfls_rt")
        )

        if return_rate != 0:
            return_rate = return_rate / 100

        else:
            return_rate = calculate_return_rate(
                average_buy_price=average_buy_price,
                current_price=current_price,
            )

        upsert_kis_holding(
            stock_code=stock_code,
            stock_name=stock_name,
            quantity=quantity,
            average_buy_price=average_buy_price,
            current_price=current_price,
            evaluation_amount=evaluation_amount,
            evaluation_profit_loss=(
                evaluation_profit_loss
            ),
            return_rate=return_rate,
        )

        current_stock_codes.append(
            stock_code
        )

        synchronized_holdings.append({
            "stock_code": stock_code,
            "stock_name": stock_name,
            "quantity": quantity,
            "average_buy_price": (
                average_buy_price
            ),
            "current_price": current_price,
            "evaluation_amount": (
                evaluation_amount
            ),
            "evaluation_profit_loss": (
                evaluation_profit_loss
            ),
            "return_rate": return_rate,
        })

    delete_missing_kis_holdings(
        current_stock_codes
    )

    return synchronized_holdings


def print_holding_sync_results(results):
    print("\n" + "#" * 80)
    print("KIS 보유 종목 DB 동기화")
    print("#" * 80)

    if not results:
        print(
            "현재 KIS 계좌에 보유 종목이 없습니다."
        )
        return

    print(
        f"동기화 종목 수: {len(results)}개"
    )

    for result in results:
        print("-" * 80)

        print(
            f"{result.get('stock_name') or ''} "
            f"({result['stock_code']})"
        )

        print(
            f"보유수량: "
            f"{result['quantity']}주"
        )

        print(
            f"평균매수가: "
            f"{result['average_buy_price']:,.0f}원"
        )

        print(
            f"현재가: "
            f"{result['current_price']:,.0f}원"
        )

        print(
            f"평가금액: "
            f"{result['evaluation_amount']:,.0f}원"
        )

        print(
            f"평가손익: "
            f"{result['evaluation_profit_loss']:+,.0f}원"
        )

        print(
            f"수익률: "
            f"{result['return_rate']:+.2%}"
        )


if __name__ == "__main__":
    sync_results = synchronize_kis_holdings()

    print_holding_sync_results(
        sync_results
    )

    print_kis_holdings()