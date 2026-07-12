from storage.database import get_connection
from strategy_management.config import initialize_strategy_config


def create_strategy_version_from_candidate(candidate_id, new_version):
    initialize_strategy_config()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            base_version,
            suggestion_text,
            status
        FROM strategy_upgrade_candidates
        WHERE id = ?
        AND status = 'approved'
    """, (
        candidate_id,
    ))

    candidate = cursor.fetchone()

    if candidate is None:
        connection.close()
        print(f"전략 버전 생성 실패: approved 상태의 후보가 아닙니다. ID {candidate_id}")
        return False

    _, base_version, suggestion_text, status = candidate

    cursor.execute("""
        INSERT INTO strategy_versions (
            version,
            name,
            description,
            is_active
        )
        VALUES (?, ?, ?, ?)
    """, (
        new_version,
        f"Strategy upgraded from {base_version}",
        suggestion_text,
        0,
    ))

    cursor.execute("""
        SELECT
            rsi_limit,
            atr_penalty_threshold,
            factor_penalty
        FROM strategy_configs
        WHERE strategy_version = ?
    """, (
        base_version,
    ))

    base_config = cursor.fetchone()

    if base_config is None:
        rsi_limit = 70
        atr_penalty_threshold = 8
        factor_penalty = -4
    else:
        rsi_limit = base_config[0]
        atr_penalty_threshold = base_config[1]
        factor_penalty = base_config[2]

    cursor.execute("""
        INSERT OR IGNORE INTO strategy_configs (
            strategy_version,
            rsi_limit,
            atr_penalty_threshold,
            factor_penalty
        )
        VALUES (?, ?, ?, ?)
    """, (
        new_version,
        rsi_limit,
        atr_penalty_threshold,
        factor_penalty,
    ))

    cursor.execute("""
        UPDATE strategy_upgrade_candidates
        SET status = 'version_created'
        WHERE id = ?
    """, (
        candidate_id,
    ))

    connection.commit()
    connection.close()

    print(f"새 전략 버전 생성 완료: {new_version}")
    print(f"후보 상태 변경 완료: ID {candidate_id} → version_created")
    return True


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="승인된 후보로부터 새 전략 버전을 생성합니다."
    )
    parser.add_argument(
        "candidate_id",
        type=int,
        help="approved 상태인 후보 ID",
    )
    parser.add_argument(
        "new_version",
        help="새 전략 버전. 예: v1.3.0",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    success = create_strategy_version_from_candidate(
        candidate_id=args.candidate_id,
        new_version=args.new_version,
    )

    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()