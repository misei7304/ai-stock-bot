import sys

from database import get_connection


def create_strategy_version_from_candidate(candidate_id, new_version):
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


if len(sys.argv) < 3:
    print("사용법: python create_strategy_version_from_candidate.py 후보ID 새버전")
    sys.exit(1)

candidate_id = int(sys.argv[1])
new_version = sys.argv[2]

create_strategy_version_from_candidate(candidate_id, new_version)