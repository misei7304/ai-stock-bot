from storage.database import get_connection


def list_strategy_config_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            strategy_version,
            old_rsi_limit,
            new_rsi_limit,
            old_atr_penalty_threshold,
            new_atr_penalty_threshold,
            old_factor_penalty,
            new_factor_penalty,
            created_at
        FROM strategy_config_history
        ORDER BY id DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()
    connection.close()

    print("\n" + "#" * 80)
    print("전략 설정 변경 이력")
    print("#" * 80)

    if not rows:
        print("변경 이력이 없습니다.")
        return

    for row in rows:
        (
            strategy_version,
            old_rsi_limit,
            new_rsi_limit,
            old_atr_penalty_threshold,
            new_atr_penalty_threshold,
            old_factor_penalty,
            new_factor_penalty,
            created_at,
        ) = row

        print(
            f"{created_at} | "
            f"{strategy_version} | "
            f"RSI {old_rsi_limit:g}→{new_rsi_limit:g} | "
            f"ATR {old_atr_penalty_threshold:g}%→{new_atr_penalty_threshold:g}% | "
            f"패널티 {old_factor_penalty:g}→{new_factor_penalty:g}"
        )


list_strategy_config_history()