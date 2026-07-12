from services.market_context_service import (
    prepare_market_context,
)
from services.performance_service import (
    run_performance_analysis,
)
from services.recommendation_service import (
    process_recommendations,
)
from services.startup_service import (
    run_startup_tasks,
)
from services.stock_analysis_service import (
    analyze_all_stocks,
)


def print_final_trade_decision(
    can_real_trade,
):
    print("\n" + "#" * 80)
    print("최종 실전 매수 판단")
    print("#" * 80)

    if can_real_trade:
        print("최종판단: 실제 매수 검토 가능")
        return

    print("최종판단: 실제 매수 금지")
    print(
        "이유: 실전 리스크 기준을 "
        "통과하지 못했습니다."
    )


def main():
    run_startup_tasks()

    market_context = prepare_market_context()

    market_result = market_context[
        "market_result"
    ]

    ai_candidates = market_context[
        "ai_candidates"
    ]

    results = analyze_all_stocks(
        ai_candidates=ai_candidates,
        market_result=market_result,
    )

    recommendation_result = (
        process_recommendations(
            results=results,
            market_result=market_result,
        )
    )

    run_performance_analysis(results)

    print_final_trade_decision(
        recommendation_result[
            "can_real_trade"
        ]
    )


if __name__ == "__main__":
    main()