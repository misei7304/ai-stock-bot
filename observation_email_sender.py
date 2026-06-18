import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv
from recommendation_reason import generate_recommendation_reason


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")


def send_observation_email(best_stock, buy_candidates, market_result):
    subject = "[AI Stock Bot] Observation Report"

    recommendation_reason = generate_recommendation_reason(
        best_stock,
        market_result
    )

    body = f"""
AI Stock Bot Observation Report

실전 매수 금지 상태입니다.
아래 종목은 실제 매수용이 아니라 관찰용 추천입니다.

[시장 상태]

시장: {market_result['market_name']}
현재가: {market_result['current_price']:,.2f}
MA20: {market_result['ma20']:,.2f}
시장 상태: {"상승장" if market_result["is_market_bull"] else "하락장 또는 약세장"}

[관찰 종목]

종목명: {best_stock['company_name']}
종목코드: {best_stock['ticker']}
현재가: {best_stock['current_price']:,.0f}원
최종점수: {best_stock['final_score']:.2f}
섹터: {best_stock['sector_name']}
현재점수: {best_stock['total_score']:.2f}
RSI: {best_stock['rsi']:.2f}
MACD: {best_stock['macd']:.2f}
MACD Signal: {best_stock['macd_signal']:.2f}
ATR%: {best_stock['atr_percent']:.2f}%
백테스트 승률: {best_stock['win_rate']:.2f}%
백테스트 평균수익: {best_stock['average_return']:.2f}%
백테스트 최종자산: {best_stock['final_money']:,.0f}원

[추천 이유]

{recommendation_reason}

[주의]

현재 실전 리스크 기준을 통과하지 못했으므로 실제 매수 금지입니다.
최소 20회 추천 기록이 쌓일 때까지 관찰만 합니다.
"""

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = EMAIL_ADDRESS
    message["To"] = TO_EMAIL

    with smtplib.SMTP("smtp.mail.me.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)

    print("관찰용 이메일 발송 완료")