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

    final_score = (
        result["total_score"] * 0.5
        + result["win_rate"] * 0.3
        + result["average_return"] * 20
    )

    result["final_score"] = final_score

    results.append(result)


print("\n" + "#" * 80)
print("현재 매수 후보 순위")
print("#" * 80)

buy_candidates = []

for stock in results:
    if stock["is_buy_candidate"]:
        buy_candidates.append(stock)

buy_candidates = sorted(
    buy_candidates,
    key=lambda x: x["final_score"],
    reverse=True
)

if len(buy_candidates) == 0:
    print("현재 매수 후보가 없습니다.")
else:
    rank = 1

    for stock in buy_candidates:
        print(
            f"{rank}위 | "
            f"{stock['company_name']} | "
            f"종목코드 {stock['ticker']} | "
            f"현재가 {stock['current_price']:,.0f}원 | "
            f"최종점수 {stock['final_score']:.2f} | "
            f"현재점수 {stock['total_score']:.2f} | "
            f"RSI {stock['rsi']:.2f} | "
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

if len(buy_candidates) == 0:
    print("현재 최종 추천 종목이 없습니다.")
else:
    best_stock = buy_candidates[0]

    print(f"최종 추천 종목: {best_stock['company_name']}")
    print(f"종목코드: {best_stock['ticker']}")
    print(f"현재가: {best_stock['current_price']:,.0f}원")
    print(f"최종점수: {best_stock['final_score']:.2f}")
    print(f"현재점수: {best_stock['total_score']:.2f}")
    print(f"RSI: {best_stock['rsi']:.2f}")
    print(f"백테스트 승률: {best_stock['win_rate']:.2f}%")
    print(f"백테스트 평균수익: {best_stock['average_return']:.2f}%")
    print(f"백테스트 최종자산: {best_stock['final_money']:,.0f}원")

    save_history(best_stock)
    send_email(best_stock, buy_candidates)


save_report(results)
analyze_history()
analyze_recommendation_performance()