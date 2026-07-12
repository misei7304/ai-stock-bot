from ai_candidate_loader import load_ai_candidates
from market_data.market import analyze_market
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


def prepare_market_context():
    print_strategy_config()

    market_result = analyze_market()
    ai_candidates = load_ai_candidates()

    print_ai_candidates(ai_candidates)

    save_ai_observations(
        ai_candidates,
        market_result,
    )

    print_market_result(market_result)

    return {
        "market_result": market_result,
        "ai_candidates": ai_candidates,
    }