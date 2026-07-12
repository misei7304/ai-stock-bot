from storage.database import get_connection
from strategy_config import initialize_strategy_config


def compare_strategy_configs():
    initialize_strategy_config()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            strategy_version,
            rsi_limit,
            atr_penalty_threshold,
            factor_penalty
        FROM strategy_configs
        ORDER BY strategy_version DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    print("\n" + "#" * 80)
    print("전략 설정 비교")
    print("#" * 80)

    if len(rows) < 2:
        print("비교 가능한 전략 설정이 부족합니다.")
        return

    current = rows[0]
    previous = rows[1]

    current_version = current[0]
    previous_version = previous[0]

    print(f"현재 버전: {current_version}")
    print(f"비교 대상: {previous_version}")
    print()

    print(f"RSI 제한: {previous[1]:g} → {current[1]:g}")
    print(f"ATR 패널티 기준: {previous[2]:g}% → {current[2]:g}%")
    print(f"팩터 패널티: {previous[3]:g} → {current[3]:g}")


compare_strategy_configs()