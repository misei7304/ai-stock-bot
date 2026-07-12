from kis.auto_sell import (
    monitor_and_sell_holdings,
    print_auto_sell_results,
)
from kis.execution_sync import (
    print_sync_results,
    synchronize_trade_executions,
)
from kis.holding_sync import (
    print_holding_sync_results,
    synchronize_kis_holdings,
)
from storage.database import initialize_database
from strategy_management.config import initialize_strategy_config
from strategy_management.version import initialize_strategy_version


def initialize_application():
    initialize_database()
    initialize_strategy_version()
    initialize_strategy_config()


def synchronize_holdings():
    try:
        holding_sync_results = synchronize_kis_holdings()

        print_holding_sync_results(
            holding_sync_results
        )

        return {
            "succeeded": True,
            "holdings": holding_sync_results,
        }

    except Exception as error:
        print("\n" + "#" * 80)
        print("KIS 보유 종목 DB 동기화 실패")
        print("#" * 80)
        print(f"오류: {error}")

        return {
            "succeeded": False,
            "holdings": [],
        }


def synchronize_executions():
    try:
        sync_results = synchronize_trade_executions()
        print_sync_results(sync_results)

        return True

    except Exception as error:
        print("\n" + "#" * 80)
        print("KIS 주문 체결 상태 동기화 실패")
        print("#" * 80)
        print(f"오류: {error}")

        return False


def monitor_auto_sell(holding_sync_result):
    if not holding_sync_result["succeeded"]:
        print("\n" + "#" * 80)
        print("KIS 자동매도 점검 차단")
        print("#" * 80)
        print(
            "이유: 보유 종목 동기화에 실패하여 "
            "계좌 보유 상태를 확인할 수 없습니다."
        )
        return False

    try:
        auto_sell_results = monitor_and_sell_holdings(
            holding_sync_result["holdings"]
        )

        print_auto_sell_results(
            auto_sell_results
        )

        return True

    except Exception as error:
        print("\n" + "#" * 80)
        print("KIS 자동매도 점검 실패")
        print("#" * 80)
        print(f"오류: {error}")

        return False


def run_startup_tasks():
    initialize_application()

    holding_sync_result = synchronize_holdings()

    synchronize_executions()

    monitor_auto_sell(
        holding_sync_result
    )

    return holding_sync_result