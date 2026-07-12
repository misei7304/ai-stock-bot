from storage.database import get_connection
from strategy_management.config import initialize_strategy_config


def list_strategy_configs():
    initialize_strategy_config()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            strategy_version,
            rsi_limit,
            atr_penalty_threshold,
            factor_penalty,
            created_at
        FROM strategy_configs
        ORDER BY strategy_version DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    print("\n" + "#" * 80)
    print("전략 설정 목록")
    print("#" * 80)

    for row in rows:
        strategy_version = row[0]
        rsi_limit = row[1]
        atr_penalty_threshold = row[2]
        factor_penalty = row[3]
        created_at = row[4]

        print(
            f"{strategy_version} | "
            f"RSI {rsi_limit:g} | "
            f"ATR {atr_penalty_threshold:g}% | "
            f"팩터패널티 {factor_penalty:g} | "
            f"{created_at}"
        )


def main():
    list_strategy_configs()


if __name__ == "__main__":
    main()