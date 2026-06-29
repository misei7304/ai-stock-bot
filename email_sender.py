import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

from risk import calculate_position


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")


def send_email(best_stock, buy_candidates, market_result):

    subject = "AI Stock Bot Daily Report"

    candidate_text = ""

    rank = 1

    for stock in buy_candidates:
        position = calculate_position(stock)

        if position["can_buy"]:
            buy_status = (
                f"매수 가능 | "
                f"{position['quantity']}주 | "
                f"투자금액 {position['investment_amount']:,.0f}원"
            )
        else:
            buy_status = "매수 불가능"

        candidate_text += (
            f"{rank}위 | "
            f"{stock['company_name']} | "
            f"{stock['ticker']} | "
            f"현재가 {stock['current_price']:,.0f}원 | "
            f"AI후보 {'예' if stock.get('is_ai_candidate') else '아니오'} | "
            f"AI확률 {stock.get('ai_probability', 0):.2%} | "
            f"최종점수 {stock['final_score']:.2f} | "
            f"RSI {stock['rsi']:.2f} | "
            f"MACD {stock['macd']:.2f} | "
            f"Signal {stock['macd_signal']:.2f} | "
            f"볼린저상단 {stock['bollinger_upper']:,.0f} | "
            f"볼린저하단 {stock['bollinger_lower']:,.0f} | "
            f"볼린저점수 {stock['bollinger_score']} | "
            f"ATR {stock['atr']:,.0f} | "
            f"ATR% {stock['atr_percent']:.2f}% | "
            f"ATR점수 {stock['atr_score']} | "
            f"승률 {stock['win_rate']:.2f}% | "
            f"평균수익 {stock['average_return']:.2f}% | "
            f"{buy_status}\n"
        )

        rank += 1

    best_position = calculate_position(best_stock)

    body = f"""
AI Stock Bot Daily Report

[시장 상황]

시장: {market_result['market_name']}
현재가: {market_result['current_price']:,.2f}
MA20: {market_result['ma20']:,.2f}
시장 상태: {"상승장" if market_result["is_market_bull"] else "하락장 또는 약세장"}

[최종 추천 종목]

종목명: {best_stock['company_name']}
종목코드: {best_stock['ticker']}
현재가: {best_stock['current_price']:,.0f}원
최종점수: {best_stock['final_score']:.2f}
AI 후보 여부: {"예" if best_stock.get("is_ai_candidate") else "아니오"}
AI 상승확률: {best_stock.get("ai_probability", 0):.2%}
현재점수: {best_stock['total_score']:.2f}
RSI: {best_stock['rsi']:.2f}
MACD: {best_stock['macd']:.2f}
MACD Signal: {best_stock['macd_signal']:.2f}
MACD Histogram: {best_stock['macd_histogram']:.2f}
볼린저 상단: {best_stock['bollinger_upper']:,.0f}원
볼린저 중간: {best_stock['bollinger_middle']:,.0f}원
볼린저 하단: {best_stock['bollinger_lower']:,.0f}원
볼린저 점수: {best_stock['bollinger_score']}
ATR: {best_stock['atr']:,.0f}원
ATR%: {best_stock['atr_percent']:.2f}%
ATR 점수: {best_stock['atr_score']}
백테스트 승률: {best_stock['win_rate']:.2f}%
백테스트 평균수익: {best_stock['average_return']:.2f}%
백테스트 최종자산: {best_stock['final_money']:,.0f}원

[리스크 관리]

총 자본: {best_position['capital']:,.0f}원
투자 비중: {best_position['risk_ratio'] * 100:.0f}%
사용 가능 금액: {best_position['available_money']:,.0f}원
매수 가능 수량: {best_position['quantity']}주
투자 금액: {best_position['investment_amount']:,.0f}원


[현재 매수 후보 순위]

{candidate_text}
"""

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = EMAIL_ADDRESS
    message["To"] = TO_EMAIL

    with smtplib.SMTP("smtp.mail.me.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)

    print("이메일 발송 완료")