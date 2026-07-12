from market_data.sector import (
    print_sector_performance,
)
from performance import (
    analyze_recommendation_performance,
)
from performance_analysis.history_analyzer import (
    analyze_history,
)
from performance_analysis.strategy_performance import (
    analyze_strategy_performance,
)
from report import save_report
from storage.database_analyzer import (
    analyze_database_recommendations,
)
from storage.performance_db import (
    update_recommendation_performance,
)


def run_base_performance_analysis(results):
    save_report(results)

    analyze_history()
    analyze_recommendation_performance()
    print_sector_performance(results)
    analyze_strategy_performance()
    analyze_database_recommendations()

    update_recommendation_performance()