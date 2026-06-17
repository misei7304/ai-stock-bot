import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")


def send_email(best_stock, buy_candidates):

    subject = "AI Stock Bot Daily Report"

    candidate_text = ""

    rank = 1

    for stock in buy_candidates:
        candidate_text += (
            f"{rank}위 | "
            f"{stock['company_name']} | "
            f"{stock['ticker']} | "
            f"현재가 {stock['current_price']:,.0f}원 | "
            f"최종점수 {stock['final_score']:.2f} | "
            f"RSI {stock['rsi']:.2f} | "
            f"승률 {stock['win_rate']:.2f}% | "
            f"평균수익 {stock['average_return']:.2f}%\n"
        )

        rank += 1

    body = f"""
AI Stock Bot Daily Report

[최종 추천 종목]

종목명: {best_stock['company_name']}
종목코드: {best_stock['ticker']}
현재가: {best_stock['current_price']:,.0f}원
최종점수: {best_stock['final_score']:.2f}
현재점수: {best_stock['total_score']:.2f}
RSI: {best_stock['rsi']:.2f}
백테스트 승률: {best_stock['win_rate']:.2f}%
백테스트 평균수익: {best_stock['average_return']:.2f}%
백테스트 최종자산: {best_stock['final_money']:,.0f}원


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