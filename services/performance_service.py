from services.ai_performance_service import (
    run_ai_performance_analysis,
)
from services.base_performance_service import (
    run_base_performance_analysis,
)
from services.factor_performance_service import (
    run_factor_performance_analysis,
)
from services.real_performance_service import (
    run_real_performance_analysis,
)
from services.strategy_performance_service import (
    run_strategy_performance_analysis,
)


def run_performance_analysis(results):
    run_base_performance_analysis(results)

    run_ai_performance_analysis()

    run_real_performance_analysis()

    run_factor_performance_analysis()

    run_strategy_performance_analysis()