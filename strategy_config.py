from database import get_connection
from strategy_version import get_current_strategy_version


def initialize_strategy_config():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_version TEXT UNIQUE NOT NULL,
            rsi_limit REAL NOT NULL,
            atr_penalty_threshold REAL NOT NULL,
            factor_penalty REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    default_configs = [
        ("v1.0.0", 70, 8, -4),
        ("v1.1.0", 65, 7, -5),
    ]

    for config in default_configs:
        cursor.execute("""
            INSERT OR IGNORE INTO strategy_configs (
                strategy_version,
                rsi_limit,
                atr_penalty_threshold,
                factor_penalty
            )
            VALUES (?, ?, ?, ?)
        """, config)

    connection.commit()
    connection.close()


def get_strategy_config():
    initialize_strategy_config()

    version = get_current_strategy_version()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            rsi_limit,
            atr_penalty_threshold,
            factor_penalty
        FROM strategy_configs
        WHERE strategy_version = ?
    """, (version,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return {
            "rsi_limit": 70,
            "atr_penalty_threshold": 8,
            "factor_penalty": -4,
        }

    return {
        "rsi_limit": row[0],
        "atr_penalty_threshold": row[1],
        "factor_penalty": row[2],
    }


def get_strategy_config_summary():
    config = get_strategy_config()

    return [
        f"RSI 제한: {config['rsi_limit']}",
        f"ATR 패널티 기준: {config['atr_penalty_threshold']}%",
        f"팩터 패널티: {config['factor_penalty']}",
    ]