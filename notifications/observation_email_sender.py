import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv
from recommendation_reason import generate_recommendation_reason
from performance_analysis.strategy_optimizer import get_strategy_optimization_suggestions
from strategy_version import get_current_strategy_version
from performance_analysis.strategy_version_performance import get_strategy_version_performance_summary
from performance_analysis.recommendation_type_performance import get_recommendation_type_performance_summary
from performance_analysis.strategy_upgrade_candidate_analyzer import get_strategy_upgrade_candidate_summary
from strategy_config import get_strategy_config_summary
from performance_analysis.strategy_version_comparison import get_strategy_version_comparison_summary
from performance_analysis.strategy_rollback_analyzer import get_strategy_rollback_analysis_summary
from strategy_config_optimizer import get_strategy_config_optimization_summary


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")


def format_observation_stock(stock, market_result, rank):
    recommendation_reason = generate_recommendation_reason(
        stock,
        market_result
    )

    return f"""
[{rank}위 관찰 종목]

종목명: {stock['company_name']}
종목코드: {stock['ticker']}
현재가: {stock['current_price']:,.0f}원
AI 후보 여부: {"예" if stock.get("is_ai_candidate") else "아니오"}
AI 상승확률: {stock.get("ai_probability", 0):.2%}
최종점수: {stock['final_score']:.2f}
섹터: {stock['sector_name']}
섹터 보너스: {stock['sector_bonus']}
적응 보너스: {stock['adaptive_bonus']}
섹터 패널티: {stock['sector_penalty']}
팩터 패널티: {stock['factor_penalty']}
이유 점수: {stock['reason_score']}
현재점수: {stock['total_score']:.2f}
RSI: {stock['rsi']:.2f}
MACD: {stock['macd']:.2f}
MACD Signal: {stock['macd_signal']:.2f}
ATR%: {stock['atr_percent']:.2f}%
백테스트 승률: {stock['win_rate']:.2f}%
백테스트 평균수익: {stock['average_return']:.2f}%
백테스트 최종자산: {stock['final_money']:,.0f}원

추천 이유:
{recommendation_reason}
"""


def send_observation_email(best_stock, buy_candidates, market_result):
    subject = "[AI Stock Bot] Observation Report"

    observation_candidates = buy_candidates[:3]

    observation_text = ""

    rank = 1

    for stock in observation_candidates:
        observation_text += format_observation_stock(
            stock,
            market_result,
            rank
        )
        rank += 1

    strategy_suggestions = "\n".join(get_strategy_optimization_suggestions())

    current_strategy_version = get_current_strategy_version()

    strategy_config_summary = "\n".join(
        get_strategy_config_summary()
    )

    strategy_version_performance = "\n".join(
        get_strategy_version_performance_summary()
    )

    strategy_version_comparison = "\n".join(
        get_strategy_version_comparison_summary()
    )

    strategy_rollback_analysis = "\n".join(
        get_strategy_rollback_analysis_summary()
    )

    strategy_config_optimization = "\n".join(
        get_strategy_config_optimization_summary()
    )

    recommendation_type_performance = "\n".join(
        get_recommendation_type_performance_summary()
    )

    strategy_upgrade_candidates = "\n".join(
        get_strategy_upgrade_candidate_summary()
    )

    body = f"""
AI Stock Bot Observation Report

실전 매수 금지 상태입니다.
아래 종목들은 실제 매수용이 아니라 관찰용 추천입니다.

[시장 상태]

시장: {market_result['market_name']}
현재가: {market_result['current_price']:,.2f}
MA20: {market_result['ma20']:,.2f}
시장 상태: {"상승장" if market_result["is_market_bull"] else "하락장 또는 약세장"}

[관찰 종목 TOP 3]
{observation_text}

[현재 전략 버전]

{current_strategy_version}

[현재 전략 설정]

{strategy_config_summary}

[전략 버전별 성과]

{strategy_version_performance}

[전략 버전 비교]

{strategy_version_comparison}

[전략 롤백 판단]

{strategy_rollback_analysis}

[전략 설정 자동 튜닝 제안]

{strategy_config_optimization}

[추천 유형별 성과]

{recommendation_type_performance}

[전략 업그레이드 후보]

{strategy_upgrade_candidates}

[자동 전략 개선 제안]

{strategy_suggestions}

[주의]

현재 실전 리스크 기준을 통과하지 못했으므로 실제 매수 금지입니다.

실전 매수 금지 이유:
- 실전 추천 기록이 아직 20회 미만입니다.
- 최근 실전 추천 성공률이 기준을 통과하지 못했습니다.
- 현재 전략 점수가 충분히 안정적이지 않습니다.
- 일부 후보는 가격이 높아 현재 자본 기준으로 실제 매수가 불가능합니다.

현재 단계에서는 실제 매수하지 않고 관찰 데이터만 누적합니다.
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