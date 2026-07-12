from report import save_report
from performance_analysis.history_analyzer import analyze_history
from performance import analyze_recommendation_performance
from performance_analysis.strategy_performance import analyze_strategy_performance
from market_data.market import analyze_market
from market_data.sector import print_sector_performance
from storage.database_analyzer import analyze_database_recommendations
from storage.performance_db import update_recommendation_performance
from performance_analysis.real_performance import analyze_real_performance
from performance_analysis.market_performance import analyze_market_performance
from performance_analysis.sector_real_performance import analyze_sector_real_performance
from performance_analysis.factor_performance import analyze_rsi_performance
from performance_analysis.factor_performance import analyze_macd_performance
from performance_analysis.factor_performance import analyze_atr_performance
from performance_analysis.factor_performance import analyze_bollinger_performance
from performance_analysis.factor_performance import analyze_final_score_performance
from performance_analysis.holding_period_performance import analyze_holding_period_performance
from performance_analysis.strategy_score import analyze_strategy_score
from performance_analysis.stock_real_performance import analyze_stock_real_performance
from performance_analysis.loss_analyzer import analyze_losing_patterns
from performance_analysis.score_adjustment_analyzer import analyze_score_adjustments
from performance_analysis.recommendation_reason_analyzer import analyze_recommendation_reason_performance
from performance_analysis.strategy_optimizer import analyze_strategy_optimization_suggestions
from strategy_management.evolution import save_strategy_evolution
from performance_analysis.strategy_evolution_analyzer import analyze_strategy_evolution_history
from performance_analysis.strategy_version_performance import analyze_strategy_version_performance
from performance_analysis.recommendation_type_performance import analyze_recommendation_type_performance
from strategy_management.upgrade_candidate import save_strategy_upgrade_candidate
from performance_analysis.strategy_upgrade_candidate_analyzer import analyze_strategy_upgrade_candidates
from strategy_management.config import get_strategy_config_summary
from performance_analysis.strategy_version_comparison import analyze_strategy_version_comparison
from performance_analysis.strategy_rollback_analyzer import analyze_strategy_rollback
from strategy_management.candidate_reviewer import review_strategy_candidates
from strategy_management.config_optimizer import analyze_strategy_config_optimization
from ai_candidate_loader import load_ai_candidates
from storage.ai_observation_database import save_ai_observations
from ai_observation_performance import update_ai_observation_performance
from performance_analysis.ai_observation_analyzer import analyze_ai_observation_performance
from performance_analysis.ai_observation_signal_analyzer import analyze_ai_observation_signal_performance
from performance_analysis.ai_observation_market_analyzer import analyze_ai_observation_market_performance
from performance_analysis.ai_observation_score_analyzer import (
    analyze_ai_observation_score,
)

from services.startup_service import run_startup_tasks
from services.stock_analysis_service import (
    analyze_all_stocks,
)
from services.recommendation_service import (
    process_recommendations,
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

save_report(results)
analyze_history()
analyze_recommendation_performance()
print_sector_performance(results)
analyze_strategy_performance()
analyze_database_recommendations()
update_recommendation_performance()
update_ai_observation_performance()
analyze_ai_observation_performance()
analyze_ai_observation_signal_performance()
analyze_ai_observation_market_performance()
analyze_ai_observation_score()
analyze_real_performance()
analyze_market_performance()
analyze_sector_real_performance()
analyze_rsi_performance()
analyze_macd_performance()
analyze_atr_performance()
analyze_bollinger_performance()
analyze_final_score_performance()
analyze_holding_period_performance()
analyze_strategy_score()
analyze_stock_real_performance()
analyze_losing_patterns()
analyze_strategy_config_optimization()
analyze_score_adjustments()
analyze_recommendation_reason_performance()
analyze_strategy_optimization_suggestions()
save_strategy_evolution()
save_strategy_upgrade_candidate()
analyze_strategy_upgrade_candidates()
review_strategy_candidates()
analyze_strategy_evolution_history()
analyze_strategy_version_performance()
analyze_strategy_version_comparison()
analyze_strategy_rollback()
analyze_recommendation_type_performance()

print("\n" + "#" * 80)
print("최종 실전 매수 판단")
print("#" * 80)

if can_real_trade:
    print("최종판단: 실제 매수 검토 가능")
else:
    print("최종판단: 실제 매수 금지")
    print("이유: 실전 리스크 기준을 통과하지 못했습니다.")