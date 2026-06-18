import pandas as pd

from data import get_stock_data
from data import calculate_indicators

from strategy import analyze_stock

from backtest import backtest
from backtest import analyze_backtest
from backtest import simulate_account

from stocks import stocks
from report import save_report
from history import save_history
from history_analyzer import analyze_history
from performance import analyze_recommendation_performance
from email_sender import send_email
from strategy_performance import analyze_strategy_performance
from risk import calculate_position
from market import analyze_market
from database import initialize_database
from database import save_recommendation_to_database
from sector import print_sector_performance
from sector import analyze_sector_performance
from sector import get_sector_name
from sector import calculate_sector_bonus
from database_analyzer import analyze_database_recommendations
from performance_db import update_recommendation_performance
from real_performance import analyze_real_performance
from market_performance import analyze_market_performance
from sector_real_performance import analyze_sector_real_performance
from factor_performance import analyze_rsi_performance
from factor_performance import analyze_macd_performance
from factor_performance import analyze_atr_performance
from factor_performance import analyze_bollinger_performance
from factor_performance import analyze_final_score_performance
from holding_period_performance import analyze_holding_period_performance
from strategy_score import analyze_strategy_score
from stock_real_performance import analyze_stock_real_performance
from real_risk_guard import check_real_risk_guard
from trade_permission import can_send_trade_email
from observation_email_sender import send_observation_email
from email_log import was_email_sent_today
from email_log import mark_email_sent_today
from recommendation_reason import generate_recommendation_reason
from adaptive_score import apply_adaptive_score
from loss_analyzer import analyze_losing_patterns
from sector_penalty import apply_sector_penalty
from factor_penalty import apply_factor_penalty
from score_adjustment_analyzer import analyze_score_adjustments
from recommendation_reason_analyzer import analyze_recommendation_reason_performance
from reason_score import apply_reason_score
from observation_database import save_observation_candidate
from strategy_optimizer import analyze_strategy_optimization_suggestions
from strategy_evolution import save_strategy_evolution
from strategy_evolution_analyzer import analyze_strategy_evolution_history
from strategy_version import initialize_strategy_version
from strategy_version import get_current_strategy_version
from strategy_version_performance import analyze_strategy_version_performance
from recommendation_type_performance import analyze_recommendation_type_performance
from strategy_upgrade_candidate import save_strategy_upgrade_candidate
from strategy_upgrade_candidate_analyzer import analyze_strategy_upgrade_candidates
from strategy_config import get_strategy_config_summary
from strategy_version_comparison import analyze_strategy_version_comparison
from strategy_rollback_analyzer import analyze_strategy_rollback
from strategy_candidate_reviewer import review_strategy_candidates


initialize_database()
initialize_strategy_version()

print("\n" + "#" * 80)
print("현재 활성 전략 설정")
print("#" * 80)

for line in get_strategy_config_summary():
    print(line)

market_result = analyze_market()

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


results = []

for ticker, company_name in stocks:
    data = get_stock_data(ticker)
    data = calculate_indicators(data)

    result = analyze_stock(data, company_name)
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

    final_score = (
        result["total_score"] * 0.5
        + result["win_rate"] * 0.3
        + result["average_return"] * 20
    )

    result["final_score"] = final_score

    results.append(result)

sector_ranking = analyze_sector_performance(results)

for stock in results:
    sector_name = get_sector_name(stock["company_name"])
    sector_bonus = calculate_sector_bonus(sector_name, sector_ranking)

    stock["sector_name"] = sector_name
    stock["sector_bonus"] = sector_bonus
    stock["final_score"] = stock["final_score"] + sector_bonus

for stock in results:
    stock = apply_adaptive_score(stock)

for stock in results:
    stock = apply_sector_penalty(stock)

for stock in results:
    stock = apply_factor_penalty(stock)

for stock in results:
    stock = apply_reason_score(stock, market_result)


print("\n" + "#" * 80)
print("현재 매수 후보 순위")
print("#" * 80)

buy_candidates = []

for stock in results:
    if stock["is_buy_candidate"] and market_result["is_market_bull"]:
        buy_candidates.append(stock)

buy_candidates = sorted(
    buy_candidates,
    key=lambda x: x["final_score"],
    reverse=True
)

if len(buy_candidates) == 0:
    print("현재 매수 후보가 없습니다.")

    if not market_result["is_market_bull"]:
        print("이유: 현재 KOSPI가 MA20 아래에 있어 시장 상태가 약세장입니다.")
else:
    rank = 1

    for stock in buy_candidates:
        print(
            f"{rank}위 | "
            f"{stock['company_name']} | "
            f"종목코드 {stock['ticker']} | "
            f"현재가 {stock['current_price']:,.0f}원 | "
            f"최종점수 {stock['final_score']:.2f} | "
            f"섹터 {stock['sector_name']} | "
            f"섹터보너스 {stock['sector_bonus']} | "
            f"적응보너스 {stock['adaptive_bonus']} | "
            f"섹터패널티 {stock['sector_penalty']} | "
            f"팩터패널티 {stock['factor_penalty']} | "
            f"이유점수 {stock['reason_score']} | "
            f"현재점수 {stock['total_score']:.2f} | "
            f"RSI {stock['rsi']:.2f} | "
            f"MACD {stock['macd']:.2f} | "
            f"MACD Signal {stock['macd_signal']:.2f} | "
            f"볼린저상단 {stock['bollinger_upper']:,.0f} | "
            f"볼린저하단 {stock['bollinger_lower']:,.0f} | "
            f"볼린저점수 {stock['bollinger_score']} | "
            f"ATR {stock['atr']:,.0f} | "
            f"ATR% {stock['atr_percent']:.2f}% | "
            f"ATR점수 {stock['atr_score']} | "
            f"승률 {stock['win_rate']:.2f}% | "
            f"평균수익 {stock['average_return']:.2f}% | "
            f"최종자산 {stock['final_money']:,.0f}원"
        )

        rank += 1


print("\n" + "#" * 80)
print("백테스트 성과 순위")
print("#" * 80)

backtest_rank = sorted(
    results,
    key=lambda x: x["final_money"],
    reverse=True
)

rank = 1

for stock in backtest_rank:
    print(
        f"{rank}위 | "
        f"{stock['company_name']} | "
        f"최종자산 {stock['final_money']:,.0f}원 | "
        f"승률 {stock['win_rate']:.2f}% | "
        f"평균수익 {stock['average_return']:.2f}% | "
        f"최악거래 {stock['worst_trade']:.2f}%"
    )

    rank += 1


print("\n" + "#" * 80)
print("최종 추천 1개")
print("#" * 80)

can_real_trade = False

affordable_candidates = []

for stock in buy_candidates:
    position = calculate_position(stock)

    if position["can_buy"]:
        stock["position"] = position
        affordable_candidates.append(stock)

if len(affordable_candidates) == 0:
    print("현재 최종 추천 가능한 종목이 없습니다.")

    if not market_result["is_market_bull"]:
        print("이유: 시장 상태가 약세장이라 매수 후보를 차단했습니다.")
    else:
        print("이유: 매수 후보는 있지만 현재 자본 기준으로 살 수 있는 종목이 없습니다.")

else:
    best_stock = affordable_candidates[0]
    position = best_stock["position"]

    print(f"최종 추천 종목: {best_stock['company_name']}")
    print(f"종목코드: {best_stock['ticker']}")
    print(f"현재가: {best_stock['current_price']:,.0f}원")
    print(f"최종점수: {best_stock['final_score']:.2f}")
    print(f"섹터: {best_stock['sector_name']}")
    print(f"섹터 보너스: {best_stock['sector_bonus']}")
    print(f"적응 보너스: {best_stock['adaptive_bonus']}")
    print(f"섹터 패널티: {best_stock['sector_penalty']}")
    print(f"팩터 패널티: {best_stock['factor_penalty']}")
    print(f"이유 점수: {best_stock['reason_score']}")
    print(f"현재점수: {best_stock['total_score']:.2f}")
    print(f"RSI: {best_stock['rsi']:.2f}")
    print(f"MACD: {best_stock['macd']:.2f}")
    print(f"MACD Signal: {best_stock['macd_signal']:.2f}")
    print(f"MACD Histogram: {best_stock['macd_histogram']:.2f}")
    print(f"볼린저 상단: {best_stock['bollinger_upper']:,.0f}원")
    print(f"볼린저 중간: {best_stock['bollinger_middle']:,.0f}원")
    print(f"볼린저 하단: {best_stock['bollinger_lower']:,.0f}원")
    print(f"볼린저 점수: {best_stock['bollinger_score']}")
    print(f"ATR: {best_stock['atr']:,.0f}원")
    print(f"ATR%: {best_stock['atr_percent']:.2f}%")
    print(f"ATR 점수: {best_stock['atr_score']}")
    print(f"백테스트 승률: {best_stock['win_rate']:.2f}%")
    print(f"백테스트 평균수익: {best_stock['average_return']:.2f}%")
    print(f"백테스트 최종자산: {best_stock['final_money']:,.0f}원")

    recommendation_reason = generate_recommendation_reason(best_stock, market_result)
    print(f"추천 이유: {recommendation_reason}")

    print("\n리스크 관리")
    print(f"총 자본: {position['capital']:,.0f}원")
    print(f"투자 비중: {position['risk_ratio'] * 100:.0f}%")
    print(f"사용 가능 금액: {position['available_money']:,.0f}원")
    print(f"매수 가능 수량: {position['quantity']}주")
    print(f"투자 금액: {position['investment_amount']:,.0f}원")

    if position["can_buy"]:
        print("매수 가능")
    else:
        print("매수 불가능")

    save_history(best_stock)
    save_recommendation_to_database(best_stock, market_result)

    can_real_trade = check_real_risk_guard()

    if was_email_sent_today():
        print("오늘 이미 이메일을 발송했습니다. 이메일 발송 생략")
    else:
        if can_send_trade_email(can_real_trade):
            send_email(best_stock, buy_candidates, market_result)
        else:
            send_observation_email(best_stock, buy_candidates, market_result)

        mark_email_sent_today()


if len(affordable_candidates) == 0:

    can_real_trade = check_real_risk_guard()

    if len(buy_candidates) > 0:
        observation_candidates = buy_candidates[:3]
        email_observation_stock = observation_candidates[0]

        for observation_stock in observation_candidates:
            position = calculate_position(observation_stock)
            observation_stock["position"] = position

            save_observation_candidate(
                observation_stock,
                market_result
            )

        if was_email_sent_today():
            print("오늘 이미 이메일을 발송했습니다. 이메일 발송 생략")
        else:
            if can_send_trade_email(can_real_trade):
                send_email(email_observation_stock, buy_candidates, market_result)
            else:
                send_observation_email(
                    email_observation_stock,
                    buy_candidates,
                    market_result
                )

            mark_email_sent_today()
    else:
        print("관찰용 이메일 발송 생략: 매수 후보가 없습니다.")

save_report(results)
analyze_history()
analyze_recommendation_performance()
print_sector_performance(results)
analyze_strategy_performance()
analyze_database_recommendations()
update_recommendation_performance()
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