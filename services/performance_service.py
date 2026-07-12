from market_data.sector import (
    print_sector_performance,
)
from performance import (
    analyze_recommendation_performance,
)
from performance_analysis.factor_performance import (
    analyze_atr_performance,
    analyze_bollinger_performance,
    analyze_final_score_performance,
    analyze_macd_performance,
    analyze_rsi_performance,
)
from performance_analysis.history_analyzer import (
    analyze_history,
)
from performance_analysis.holding_period_performance import (
    analyze_holding_period_performance,
)
from performance_analysis.loss_analyzer import (
    analyze_losing_patterns,
)
from performance_analysis.market_performance import (
    analyze_market_performance,
)
from performance_analysis.real_performance import (
    analyze_real_performance,
)
from performance_analysis.recommendation_reason_analyzer import (
    analyze_recommendation_reason_performance,
)
from performance_analysis.recommendation_type_performance import (
    analyze_recommendation_type_performance,
)
from performance_analysis.score_adjustment_analyzer import (
    analyze_score_adjustments,
)
from performance_analysis.sector_real_performance import (
    analyze_sector_real_performance,
)
from performance_analysis.stock_real_performance import (
    analyze_stock_real_performance,
)
from performance_analysis.strategy_evolution_analyzer import (
    analyze_strategy_evolution_history,
)
from performance_analysis.strategy_optimizer import (
    analyze_strategy_optimization_suggestions,
)
from performance_analysis.strategy_performance import (
    analyze_strategy_performance,
)
from performance_analysis.strategy_rollback_analyzer import (
    analyze_strategy_rollback,
)
from performance_analysis.strategy_score import (
    analyze_strategy_score,
)
from performance_analysis.strategy_upgrade_candidate_analyzer import (
    analyze_strategy_upgrade_candidates,
)
from performance_analysis.strategy_version_comparison import (
    analyze_strategy_version_comparison,
)
from performance_analysis.strategy_version_performance import (
    analyze_strategy_version_performance,
)
from report import save_report
from storage.database_analyzer import (
    analyze_database_recommendations,
)
from storage.performance_db import (
    update_recommendation_performance,
)
from strategy_management.candidate_reviewer import (
    review_strategy_candidates,
)
from strategy_management.config_optimizer import (
    analyze_strategy_config_optimization,
)
from strategy_management.evolution import (
    save_strategy_evolution,
)
from strategy_management.upgrade_candidate import (
    save_strategy_upgrade_candidate,
)

from services.ai_performance_service import (
    run_ai_performance_analysis,
)


def run_performance_analysis(results):
    save_report(results)

    analyze_history()
    analyze_recommendation_performance()
    print_sector_performance(results)
    analyze_strategy_performance()
    analyze_database_recommendations()

    update_recommendation_performance()

    run_ai_performance_analysis()

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