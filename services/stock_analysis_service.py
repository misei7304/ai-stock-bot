import pandas as pd

from ai_candidate_loader import (
    get_ai_probability,
    is_ai_candidate,
)
from backtest import (
    analyze_backtest,
    backtest,
    simulate_account,
)
from market_data.data import (
    calculate_indicators,
    get_stock_data,
)
from market_data.sector import (
    analyze_sector_performance,
    calculate_sector_bonus,
    get_sector_name,
)
from market_data.stocks import stocks
from scoring.adaptive_score import apply_adaptive_score
from scoring.factor_penalty import apply_factor_penalty
from scoring.reason_score import apply_reason_score
from scoring.sector_penalty import apply_sector_penalty
from strategies.stock_strategy import analyze_stock


def analyze_single_stock(
    ticker,
    company_name,
    ai_candidates,
):
    data = get_stock_data(ticker)
    data = calculate_indicators(data)

    result = analyze_stock(
        data,
        company_name,
    )

    result["ticker"] = ticker

    trades = backtest(data)

    backtest_result = analyze_backtest(trades)
    account_result = simulate_account(trades)

    result["trade_count"] = backtest_result["trade_count"]
    result["win_rate"] = backtest_result["win_rate"]
    result["average_return"] = backtest_result["average_return"]
    result["total_return"] = backtest_result["total_return"]
    result["best_trade"] = backtest_result["best_trade"]
    result["worst_trade"] = backtest_result["worst_trade"]

    result["final_money"] = account_result["final_money"]
    result["profit"] = account_result["profit"]

    if pd.isna(result["total_score"]):
        result["total_score"] = 0

    result["final_score"] = (
        result["total_score"] * 0.5
        + result["win_rate"] * 0.3
        + result["average_return"] * 20
    )

    result["is_ai_candidate"] = is_ai_candidate(
        ticker,
        ai_candidates,
    )

    result["ai_probability"] = get_ai_probability(
        ticker,
        ai_candidates,
    )

    result["ai_bonus"] = 0

    if result["is_ai_candidate"]:
        result["ai_bonus"] = (
            result["ai_probability"] * 30
        )

        result["final_score"] += result["ai_bonus"]

    return result


def apply_sector_scores(results):
    sector_ranking = analyze_sector_performance(
        results
    )

    for stock in results:
        sector_name = get_sector_name(
            stock["company_name"]
        )

        sector_bonus = calculate_sector_bonus(
            sector_name,
            sector_ranking,
        )

        stock["sector_name"] = sector_name
        stock["sector_bonus"] = sector_bonus
        stock["final_score"] += sector_bonus

    return results


def apply_score_adjustments(
    results,
    market_result,
):
    for stock in results:
        apply_adaptive_score(stock)
        apply_sector_penalty(stock)
        apply_factor_penalty(stock)
        apply_reason_score(
            stock,
            market_result,
        )

    return results


def analyze_all_stocks(
    ai_candidates,
    market_result,
):
    results = []

    for ticker, company_name in stocks:
        result = analyze_single_stock(
            ticker=ticker,
            company_name=company_name,
            ai_candidates=ai_candidates,
        )

        results.append(result)

    apply_sector_scores(results)

    apply_score_adjustments(
        results,
        market_result,
    )

    return results