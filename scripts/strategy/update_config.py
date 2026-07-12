from storage.database import get_connection
from strategy_management.config import initialize_strategy_config
from strategy_management.config_history import save_strategy_config_history


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

    if (
        old_rsi_limit == rsi_limit
        and old_atr_penalty_threshold == atr_penalty_threshold
        and old_factor_penalty == factor_penalty
    ):
        connection.close()

        print(
            f"전략 설정 수정 생략: "
            f"{strategy_version} 설정이 기존 값과 같습니다."
        )
        return True

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


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="특정 전략 버전의 설정을 수정합니다."
    )
    parser.add_argument(
        "strategy_version",
        help="수정할 전략 버전. 예: v1.2.0",
    )
    parser.add_argument(
        "rsi_limit",
        type=float,
        help="새 RSI 제한",
    )
    parser.add_argument(
        "atr_penalty_threshold",
        type=float,
        help="새 ATR 패널티 기준",
    )
    parser.add_argument(
        "factor_penalty",
        type=float,
        help="새 팩터 패널티",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    success = update_strategy_config(
        strategy_version=args.strategy_version,
        rsi_limit=args.rsi_limit,
        atr_penalty_threshold=args.atr_penalty_threshold,
        factor_penalty=args.factor_penalty,
    )

    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()