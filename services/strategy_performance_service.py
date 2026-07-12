from performance_analysis.recommendation_reason_analyzer import (
    analyze_recommendation_reason_performance,
)
from performance_analysis.recommendation_type_performance import (
    analyze_recommendation_type_performance,
)
from performance_analysis.score_adjustment_analyzer import (
    analyze_score_adjustments,
)
from performance_analysis.strategy_evolution_analyzer import (
    analyze_strategy_evolution_history,
)
from performance_analysis.strategy_optimizer import (
    analyze_strategy_optimization_suggestions,
)
from performance_analysis.strategy_rollback_analyzer import (
    analyze_strategy_rollback,
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


def run_strategy_performance_analysis():
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