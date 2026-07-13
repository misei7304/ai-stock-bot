from ai_candidate_loader import (
    convert_scan_results_to_ai_candidates,
    load_ai_candidates,
)
from market_data.market import analyze_market
from ml.scan_stocks_model import (
    scan_stocks_model,
)
from storage.ai_observation_database import (
    save_ai_observations,
)
from strategy_management.config import (
    get_strategy_config_summary,
)


def print_strategy_config():
    print("\n" + "#" * 80)
    print("현재 활성 전략 설정")
    print("#" * 80)

    for line in get_strategy_config_summary():
        print(line)


def print_ai_candidates(ai_candidates):
    print("\n" + "#" * 80)
    print("AI 모델 후보")
    print("#" * 80)

    if len(ai_candidates) == 0:
        print("AI 후보가 없습니다.")
        return

    for candidate in ai_candidates:
        print(
            f"{candidate['ticker']} | "
            f"AI 상승확률 "
            f"{candidate['ai_probability']:.2%} | "
            f"기준일 {candidate['ai_date']} | "
            f"기준가 "
            f"{candidate['ai_close']:,.0f}원"
        )


def print_market_result(market_result):
    print("\n" + "#" * 80)
    print("시장 상황 분석")
    print("#" * 80)

    print(
        f"시장: "
        f"{market_result['market_name']}"
    )
    print(
        f"현재가: "
        f"{market_result['current_price']:,.2f}"
    )
    print(
        f"MA20: "
        f"{market_result['ma20']:,.2f}"
    )

    if market_result["is_market_bull"]:
        print("시장 상태: 상승장")
    else:
        print("시장 상태: 하락장 또는 약세장")


def refresh_ai_candidates():
    print("\n" + "#" * 80)
    print("AI 종목 스캔")
    print("#" * 80)

    try:
        scan_results = scan_stocks_model()

        print(
            "AI 종목 스캔 완료: "
            f"{len(scan_results)}개 후보 저장"
        )

        return {
            "succeeded": True,
            "scan_results": scan_results,
            "error": None,
        }

    except Exception as error:
        print("AI 종목 스캔 실패")
        print(f"오류: {error}")

        return {
            "succeeded": False,
            "scan_results": [],
            "error": str(error),
        }


def prepare_market_context():
    print_strategy_config()

    market_result = analyze_market()

    scan_result = refresh_ai_candidates()

    if scan_result["succeeded"]:
        ai_candidates = (
            convert_scan_results_to_ai_candidates(
                scan_result["scan_results"]
            )
        )

        ai_candidate_source = (
            "fresh_scan"
        )

    else:
        print(
            "AI 스캔에 실패하여 기존의 유효한 "
            "AI 후보 파일을 사용합니다."
        )

        ai_candidates = load_ai_candidates()

        ai_candidate_source = (
            "csv_fallback"
        )

    print_ai_candidates(
        ai_candidates
    )

    print(
        "AI 후보 데이터 출처: "
        f"{ai_candidate_source}"
    )

    save_ai_observations(
        ai_candidates,
        market_result,
    )

    print_market_result(
        market_result
    )

    return {
        "market_result": market_result,
        "ai_candidates": ai_candidates,
        "ai_scan_succeeded": (
            scan_result["succeeded"]
        ),
        "ai_scan_error": (
            scan_result["error"]
        ),
        "ai_candidate_source": (
            ai_candidate_source
        ),
    }