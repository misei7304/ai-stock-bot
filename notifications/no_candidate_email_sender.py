import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv
from strategy_management.version import get_current_strategy_version
from strategy_management.config import get_strategy_config_summary
from performance_analysis.strategy_version_performance import get_strategy_version_performance_summary
from performance_analysis.strategy_version_comparison import get_strategy_version_comparison_summary
from performance_analysis.strategy_rollback_analyzer import get_strategy_rollback_analysis_summary
from strategy_management.config_optimizer import get_strategy_config_optimization_summary
from performance_analysis.recommendation_type_performance import get_recommendation_type_performance_summary
from performance_analysis.strategy_upgrade_candidate_analyzer import get_strategy_upgrade_candidate_summary
from performance_analysis.strategy_optimizer import get_strategy_optimization_suggestions
from ai_candidate_loader import load_ai_candidates


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")


def send_no_candidate_email(market_result):
    subject = "[AI Stock Bot] No Candidate Report"

    ai_candidates = load_ai_candidates()

    if len(ai_candidates) == 0:
        ai_candidate_text = "AI 후보가 없습니다."
    else:
        ai_candidate_text = ""

        rank = 1

        for candidate in ai_candidates:
            ai_candidate_text += (
                f"{rank}위 | "
                f"종목코드 {candidate['ticker']} | "
                f"AI 상승확률 {candidate['ai_probability']:.2%} | "
                f"기준일 {candidate['ai_date']} | "
                f"기준가 {candidate['ai_close']:,.0f}원\n"
            )
            rank += 1

    body = f"""
AI Stock Bot No Candidate Report

오늘은 매수 후보가 없습니다.
실제 매수도 하지 않습니다.

[AI 모델 관찰 후보]

{ai_candidate_text}

주의: 위 AI 후보는 실제 매수 후보가 아닙니다.
현재 시장 상태와 리스크 기준을 통과해야 실제 매수 검토가 가능합니다.

[시장 상태]

시장: {market_result['market_name']}
현재가: {market_result['current_price']:,.2f}
MA20: {market_result['ma20']:,.2f}
시장 상태: {"상승장" if market_result["is_market_bull"] else "하락장 또는 약세장"}

[현재 전략 버전]

{get_current_strategy_version()}

[현재 전략 설정]

{chr(10).join(get_strategy_config_summary())}

[전략 버전별 성과]

{chr(10).join(get_strategy_version_performance_summary())}

[전략 버전 비교]

{chr(10).join(get_strategy_version_comparison_summary())}

[전략 롤백 판단]

{chr(10).join(get_strategy_rollback_analysis_summary())}

[전략 설정 자동 튜닝 제안]

{chr(10).join(get_strategy_config_optimization_summary())}

[추천 유형별 성과]

{chr(10).join(get_recommendation_type_performance_summary())}

[전략 업그레이드 후보]

{chr(10).join(get_strategy_upgrade_candidate_summary())}

[자동 전략 개선 제안]

{chr(10).join(get_strategy_optimization_suggestions())}

[주의]

오늘은 조건을 통과한 매수 후보가 없으므로 관찰 이메일만 발송합니다.
현재 단계에서는 실제 매수하지 않고 데이터만 누적합니다.
"""

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = EMAIL_ADDRESS
    message["To"] = TO_EMAIL

    with smtplib.SMTP("smtp.mail.me.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)

    print("매수 후보 없음 이메일 발송 완료")