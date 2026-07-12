from history import save_history
from kis.auto_trade_bridge import (
    execute_candidate_auto_buy,
    print_bridge_result,
)
from notifications.email_log import (
    mark_email_sent_today,
    was_email_sent_today,
)
from notifications.email_sender import send_email
from notifications.no_candidate_email_sender import (
    send_no_candidate_email,
)
from notifications.observation_email_sender import (
    send_observation_email,
)
from scoring.recommendation_reason import (
    generate_recommendation_reason,
)
from storage.database import (
    save_recommendation_to_database,
)
from storage.observation_database import (
    save_observation_candidate,
)
from trading.real_risk_guard import (
    check_real_risk_guard,
)
from trading.risk_manager import calculate_position
from trading.trade_permission import can_send_trade_email


def select_buy_candidates(
    results,
    market_result,
):
    if not market_result["is_market_bull"]:
        return []

    return sorted(
        [
            stock
            for stock in results
            if stock["is_buy_candidate"]
        ],
        key=lambda stock: stock["final_score"],
        reverse=True,
    )


def print_buy_candidates(
    buy_candidates,
    market_result,
):
    print("\n" + "#" * 80)
    print("현재 매수 후보 순위")
    print("#" * 80)

    if len(buy_candidates) == 0:
        print("현재 매수 후보가 없습니다.")

        if not market_result["is_market_bull"]:
            print(
                "이유: 현재 KOSPI가 MA20 아래에 있어 "
                "시장 상태가 약세장입니다."
            )

        return

    for rank, stock in enumerate(
        buy_candidates,
        start=1,
    ):
        print(
            f"{rank}위 | "
            f"{stock['company_name']} | "
            f"종목코드 {stock['ticker']} | "
            f"현재가 {stock['current_price']:,.0f}원 | "
            f"최종점수 {stock['final_score']:.2f} | "
            f"AI후보 "
            f"{'예' if stock.get('is_ai_candidate') else '아니오'} | "
            f"AI확률 "
            f"{stock.get('ai_probability', 0):.2%} | "
            f"AI보너스 "
            f"{stock.get('ai_bonus', 0):.2f} | "
            f"섹터 {stock['sector_name']} | "
            f"섹터보너스 {stock['sector_bonus']} | "
            f"적응보너스 {stock['adaptive_bonus']} | "
            f"섹터패널티 {stock['sector_penalty']} | "
            f"팩터패널티 {stock['factor_penalty']} | "
            f"이유점수 {stock['reason_score']} | "
            f"현재점수 {stock['total_score']:.2f} | "
            f"RSI {stock['rsi']:.2f} | "
            f"MACD {stock['macd']:.2f} | "
            f"MACD Signal "
            f"{stock['macd_signal']:.2f} | "
            f"볼린저상단 "
            f"{stock['bollinger_upper']:,.0f} | "
            f"볼린저하단 "
            f"{stock['bollinger_lower']:,.0f} | "
            f"볼린저점수 "
            f"{stock['bollinger_score']} | "
            f"ATR {stock['atr']:,.0f} | "
            f"ATR% {stock['atr_percent']:.2f}% | "
            f"ATR점수 {stock['atr_score']} | "
            f"승률 {stock['win_rate']:.2f}% | "
            f"평균수익 "
            f"{stock['average_return']:.2f}% | "
            f"최종자산 "
            f"{stock['final_money']:,.0f}원"
        )


def print_backtest_ranking(results):
    print("\n" + "#" * 80)
    print("백테스트 성과 순위")
    print("#" * 80)

    backtest_rank = sorted(
        results,
        key=lambda stock: stock["final_money"],
        reverse=True,
    )

    for rank, stock in enumerate(
        backtest_rank,
        start=1,
    ):
        print(
            f"{rank}위 | "
            f"{stock['company_name']} | "
            f"최종자산 "
            f"{stock['final_money']:,.0f}원 | "
            f"승률 {stock['win_rate']:.2f}% | "
            f"평균수익 "
            f"{stock['average_return']:.2f}% | "
            f"최악거래 "
            f"{stock['worst_trade']:.2f}%"
        )


def select_affordable_candidates(
    buy_candidates,
):
    affordable_candidates = []

    for stock in buy_candidates:
        position = calculate_position(stock)

        if not position["can_buy"]:
            continue

        stock["position"] = position
        affordable_candidates.append(stock)

    return affordable_candidates


def print_best_stock(
    best_stock,
    market_result,
):
    position = best_stock["position"]

    print(f"최종 추천 종목: {best_stock['company_name']}")
    print(f"종목코드: {best_stock['ticker']}")
    print(
        f"현재가: "
        f"{best_stock['current_price']:,.0f}원"
    )
    print(
        f"최종점수: "
        f"{best_stock['final_score']:.2f}"
    )
    print(
        "AI 후보 여부: "
        f"{'예' if best_stock.get('is_ai_candidate') else '아니오'}"
    )
    print(
        "AI 상승확률: "
        f"{best_stock.get('ai_probability', 0):.2%}"
    )
    print(
        "AI 보너스: "
        f"{best_stock.get('ai_bonus', 0):.2f}"
    )
    print(f"섹터: {best_stock['sector_name']}")
    print(
        f"섹터 보너스: "
        f"{best_stock['sector_bonus']}"
    )
    print(
        f"적응 보너스: "
        f"{best_stock['adaptive_bonus']}"
    )
    print(
        f"섹터 패널티: "
        f"{best_stock['sector_penalty']}"
    )
    print(
        f"팩터 패널티: "
        f"{best_stock['factor_penalty']}"
    )
    print(
        f"이유 점수: "
        f"{best_stock['reason_score']}"
    )
    print(
        f"현재점수: "
        f"{best_stock['total_score']:.2f}"
    )
    print(f"RSI: {best_stock['rsi']:.2f}")
    print(f"MACD: {best_stock['macd']:.2f}")
    print(
        f"MACD Signal: "
        f"{best_stock['macd_signal']:.2f}"
    )
    print(
        f"MACD Histogram: "
        f"{best_stock['macd_histogram']:.2f}"
    )
    print(
        f"볼린저 상단: "
        f"{best_stock['bollinger_upper']:,.0f}원"
    )
    print(
        f"볼린저 중간: "
        f"{best_stock['bollinger_middle']:,.0f}원"
    )
    print(
        f"볼린저 하단: "
        f"{best_stock['bollinger_lower']:,.0f}원"
    )
    print(
        f"볼린저 점수: "
        f"{best_stock['bollinger_score']}"
    )
    print(
        f"ATR: "
        f"{best_stock['atr']:,.0f}원"
    )
    print(
        f"ATR%: "
        f"{best_stock['atr_percent']:.2f}%"
    )
    print(
        f"ATR 점수: "
        f"{best_stock['atr_score']}"
    )
    print(
        f"백테스트 승률: "
        f"{best_stock['win_rate']:.2f}%"
    )
    print(
        f"백테스트 평균수익: "
        f"{best_stock['average_return']:.2f}%"
    )
    print(
        f"백테스트 최종자산: "
        f"{best_stock['final_money']:,.0f}원"
    )

    recommendation_reason = (
        generate_recommendation_reason(
            best_stock,
            market_result,
        )
    )

    print(f"추천 이유: {recommendation_reason}")

    print("\n리스크 관리")
    print(
        f"총 자본: "
        f"{position['capital']:,.0f}원"
    )
    print(
        f"투자 비중: "
        f"{position['risk_ratio'] * 100:.0f}%"
    )
    print(
        f"사용 가능 금액: "
        f"{position['available_money']:,.0f}원"
    )
    print(
        f"매수 가능 수량: "
        f"{position['quantity']}주"
    )
    print(
        f"투자 금액: "
        f"{position['investment_amount']:,.0f}원"
    )
    print("매수 가능")


def execute_auto_trade_if_allowed(
    best_stock,
    market_result,
    can_real_trade,
):
    print("\n" + "#" * 80)
    print("KIS 자동매매 판단")
    print("#" * 80)

    if not can_real_trade:
        print("자동매매 실행 안 함")
        print(
            "이유: 실전 리스크 가드가 "
            "매수를 허용하지 않았습니다."
        )
        return None

    if not best_stock.get("is_ai_candidate"):
        print("자동매매 실행 안 함")
        print(
            "이유: 최종 추천 종목이 "
            "AI 후보가 아닙니다."
        )
        return None

    try:
        auto_trade_result = execute_candidate_auto_buy(
            ticker=best_stock["ticker"],
            ai_probability=best_stock.get(
                "ai_probability",
                0,
            ),
            market_is_bull=market_result[
                "is_market_bull"
            ],
            risk_allowed=can_real_trade,
            stock_name=best_stock[
                "company_name"
            ],
        )

        print_bridge_result(auto_trade_result)

        return auto_trade_result

    except Exception as error:
        print("KIS 자동매매 실행 실패")
        print(f"오류: {error}")

        return None


def send_candidate_email(
    stock,
    buy_candidates,
    market_result,
    can_real_trade,
):
    if was_email_sent_today():
        print(
            "오늘 이미 이메일을 발송했습니다. "
            "이메일 발송 생략"
        )
        return False

    if can_send_trade_email(can_real_trade):
        send_email(
            stock,
            buy_candidates,
            market_result,
        )
    else:
        send_observation_email(
            stock,
            buy_candidates,
            market_result,
        )

    mark_email_sent_today()

    return True


def process_no_affordable_candidate(
    buy_candidates,
    market_result,
    can_real_trade,
):
    if len(buy_candidates) > 0:
        observation_candidates = buy_candidates[:3]
        email_observation_stock = (
            observation_candidates[0]
        )

        for observation_stock in observation_candidates:
            position = calculate_position(
                observation_stock
            )

            observation_stock["position"] = position

            save_observation_candidate(
                observation_stock,
                market_result,
            )

        send_candidate_email(
            stock=email_observation_stock,
            buy_candidates=buy_candidates,
            market_result=market_result,
            can_real_trade=can_real_trade,
        )

        return

    if was_email_sent_today():
        print(
            "오늘 이미 이메일을 발송했습니다. "
            "이메일 발송 생략"
        )
        return

    send_no_candidate_email(market_result)
    mark_email_sent_today()


def process_recommendations(
    results,
    market_result,
):
    buy_candidates = select_buy_candidates(
        results,
        market_result,
    )

    print_buy_candidates(
        buy_candidates,
        market_result,
    )

    print_backtest_ranking(results)

    print("\n" + "#" * 80)
    print("최종 추천 1개")
    print("#" * 80)

    affordable_candidates = (
        select_affordable_candidates(
            buy_candidates
        )
    )

    can_real_trade = False
    best_stock = None

    if len(affordable_candidates) == 0:
        print(
            "현재 최종 추천 가능한 종목이 없습니다."
        )

        if not market_result["is_market_bull"]:
            print(
                "이유: 시장 상태가 약세장이라 "
                "매수 후보를 차단했습니다."
            )
        else:
            print(
                "이유: 매수 후보는 있지만 "
                "현재 자본 기준으로 살 수 있는 "
                "종목이 없습니다."
            )

        can_real_trade = check_real_risk_guard()

        process_no_affordable_candidate(
            buy_candidates=buy_candidates,
            market_result=market_result,
            can_real_trade=can_real_trade,
        )

    else:
        best_stock = affordable_candidates[0]

        print_best_stock(
            best_stock,
            market_result,
        )

        save_history(best_stock)

        save_recommendation_to_database(
            best_stock,
            market_result,
        )

        can_real_trade = check_real_risk_guard()

        execute_auto_trade_if_allowed(
            best_stock=best_stock,
            market_result=market_result,
            can_real_trade=can_real_trade,
        )

        send_candidate_email(
            stock=best_stock,
            buy_candidates=buy_candidates,
            market_result=market_result,
            can_real_trade=can_real_trade,
        )

    return {
        "buy_candidates": buy_candidates,
        "affordable_candidates": affordable_candidates,
        "best_stock": best_stock,
        "can_real_trade": can_real_trade,
    }