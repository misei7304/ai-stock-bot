from market_data.market import analyze_market
from strategy_management.config import get_strategy_config_summary
from ai_candidate_loader import load_ai_candidates
from storage.ai_observation_database import save_ai_observations

from services.startup_service import run_startup_tasks
from services.stock_analysis_service import (
    analyze_all_stocks,
)
from services.recommendation_service import (
    process_recommendations,
)
from services.performance_service import (
    run_performance_analysis,
)


run_startup_tasks()

print("\n" + "#" * 80)
print("현재 활성 전략 설정")
print("#" * 80)

for line in get_strategy_config_summary():
    print(line)

market_result = analyze_market()

ai_candidates = load_ai_candidates()

print("\n" + "#" * 80)
print("AI 모델 후보")
print("#" * 80)

if len(ai_candidates) == 0:
    print("AI 후보가 없습니다.")
else:
    for candidate in ai_candidates:
        print(
            f"{candidate['ticker']} | "
            f"AI 상승확률 {candidate['ai_probability']:.2%} | "
            f"기준일 {candidate['ai_date']} | "
            f"기준가 {candidate['ai_close']:,.0f}원"
        )

save_ai_observations(ai_candidates, market_result)

print("\n" + "#" * 80)
print("시장 상황 분석")
print("#" * 80)

print(f"시장: {market_result['market_name']}")
print(f"현재가: {market_result['current_price']:,.2f}")
print(f"MA20: {market_result['ma20']:,.2f}")

if market_result["is_market_bull"]:
    print("시장 상태: 상승장")
else:
    print("시장 상태: 하락장 또는 약세장")


results = analyze_all_stocks(
    ai_candidates=ai_candidates,
    market_result=market_result,
)

recommendation_result = process_recommendations(
    results=results,
    market_result=market_result,
)

can_real_trade = recommendation_result[
    "can_real_trade"
]

run_performance_analysis(results)

print("\n" + "#" * 80)
print("최종 실전 매수 판단")
print("#" * 80)

if can_real_trade:
    print("최종판단: 실제 매수 검토 가능")
else:
    print("최종판단: 실제 매수 금지")
    print("이유: 실전 리스크 기준을 통과하지 못했습니다.")