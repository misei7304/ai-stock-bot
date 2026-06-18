from database import get_connection


def save_strategy_config_history(
    strategy_version,
    old_rsi_limit,
    new_rsi_limit,
    old_atr_penalty_threshold,
    new_atr_penalty_threshold,
    old_factor_penalty,
    new_factor_penalty,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_config_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_version TEXT NOT NULL,
            old_rsi_limit REAL,
            new_rsi_limit REAL,
            old_atr_penalty_threshold REAL,
            new_atr_penalty_threshold REAL,
            old_factor_penalty REAL,
            new_factor_penalty REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        INSERT INTO strategy_config_history (
            strategy_version,
            old_rsi_limit,
            new_rsi_limit,
            old_atr_penalty_threshold,
            new_atr_penalty_threshold,
            old_factor_penalty,
            new_factor_penalty
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        strategy_version,
        old_rsi_limit,
        new_rsi_limit,
        old_atr_penalty_threshold,
        new_atr_penalty_threshold,
        old_factor_penalty,
        new_factor_penalty,
    ))

    connection.commit()
    connection.close()

    print("전략 설정 변경 이력 저장 완료")