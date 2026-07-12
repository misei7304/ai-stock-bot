from ai_observation_performance import (
    update_ai_observation_performance,
)
from performance_analysis.ai_observation_analyzer import (
    analyze_ai_observation_performance,
)
from performance_analysis.ai_observation_market_analyzer import (
    analyze_ai_observation_market_performance,
)
from performance_analysis.ai_observation_score_analyzer import (
    analyze_ai_observation_score,
)
from performance_analysis.ai_observation_signal_analyzer import (
    analyze_ai_observation_signal_performance,
)


def run_ai_performance_analysis():
    update_ai_observation_performance()

    analyze_ai_observation_performance()
    analyze_ai_observation_signal_performance()
    analyze_ai_observation_market_performance()
    analyze_ai_observation_score()