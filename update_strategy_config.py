import sys

from database import get_connection
from strategy_config import initialize_strategy_config
from strategy_config_history import save_strategy_config_history


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
        SELECT
            rsi_limit,
            atr_penalty_threshold,
            factor_penalty
        FROM strategy_configs
        WHERE strategy_version = ?
    """, (
        strategy_version,
    ))

    old_config = cursor.fetchone()

    if old_config is None:
        connection.close()
        print(f"전략 설정 수정 실패: {strategy_version} 없음")
        return False

    old_rsi_limit = old_config[0]
    old_atr_penalty_threshold = old_config[1]
    old_factor_penalty = old_config[2]

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
    connection.close()

    save_strategy_config_history(
        strategy_version,
        old_rsi_limit,
        rsi_limit,
        old_atr_penalty_threshold,
        atr_penalty_threshold,
        old_factor_penalty,
        factor_penalty,
    )

    print(f"전략 설정 수정 완료: {strategy_version}")
    print(f"RSI 제한: {old_rsi_limit:g} → {rsi_limit:g}")
    print(f"ATR 패널티 기준: {old_atr_penalty_threshold:g}% → {atr_penalty_threshold:g}%")
    print(f"팩터 패널티: {old_factor_penalty:g} → {factor_penalty:g}")

    return True


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