import sys

from database import get_connection
from strategy_config import initialize_strategy_config


def update_strategy_config(
    strategy_version,
    rsi_limit,
    atr_penalty_threshold,
    factor_penalty,
):
    initialize_strategy_config()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE strategy_configs
        SET
            rsi_limit = ?,
            atr_penalty_threshold = ?,
            factor_penalty = ?
        WHERE strategy_version = ?
    """, (
        rsi_limit,
        atr_penalty_threshold,
        factor_penalty,
        strategy_version,
    ))

    connection.commit()

    if cursor.rowcount == 0:
        print(f"전략 설정 수정 실패: {strategy_version} 없음")
    else:
        print(f"전략 설정 수정 완료: {strategy_version}")
        print(f"RSI 제한: {rsi_limit}")
        print(f"ATR 패널티 기준: {atr_penalty_threshold}%")
        print(f"팩터 패널티: {factor_penalty}")

    connection.close()


if len(sys.argv) != 5:
    print(
        "사용법: python update_strategy_config.py 버전 RSI ATR패널티기준 팩터패널티"
    )
    sys.exit(1)

strategy_version = sys.argv[1]
rsi_limit = float(sys.argv[2])
atr_penalty_threshold = float(sys.argv[3])
factor_penalty = float(sys.argv[4])

update_strategy_config(
    strategy_version,
    rsi_limit,
    atr_penalty_threshold,
    factor_penalty,
)