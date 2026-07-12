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
from performance_analysis.sector_real_performance import (
    analyze_sector_real_performance,
)
from performance_analysis.stock_real_performance import (
    analyze_stock_real_performance,
)
from performance_analysis.strategy_score import (
    analyze_strategy_score,
)


def run_real_performance_analysis():
    analyze_real_performance()
    analyze_market_performance()
    analyze_sector_real_performance()

    analyze_holding_period_performance()
    analyze_strategy_score()
    analyze_stock_real_performance()
    analyze_losing_patterns()