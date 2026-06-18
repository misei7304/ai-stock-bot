from database import get_connection


def create_next_strategy_version_from_candidate(candidate_id):
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
    """, (candidate_id,))

    candidate = cursor.fetchone()

    if candidate is None:
        print("해당 전략 업그레이드 후보를 찾을 수 없습니다.")
        connection.close()
        return False

    candidate_id, base_version, suggestion_text, status = candidate

    if status != "approved":
        print("approved 상태인 후보만 새 전략 버전으로 만들 수 있습니다.")
        connection.close()
        return False

    cursor.execute("""
        SELECT version
        FROM strategy_versions
        ORDER BY id DESC
        LIMIT 1
    """)

    latest_row = cursor.fetchone()

    if latest_row is None:
        new_version = "v1.0.0"
    else:
        latest_version = latest_row[0]
        version_number = latest_version.replace("v", "")
        major, minor, patch = version_number.split(".")

        major = int(major)
        minor = int(minor)
        patch = int(patch)

        minor += 1
        patch = 0

        new_version = f"v{major}.{minor}.{patch}"

    new_name = f"Strategy upgraded from {base_version}"

    new_description = f"""
자동 생성된 전략 업그레이드 버전입니다.

기반 버전:
{base_version}

반영 예정 제안:
{suggestion_text}
"""

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
        new_name,
        new_description,
        0,
    ))

    cursor.execute("""
        UPDATE strategy_upgrade_candidates
        SET status = 'version_created'
        WHERE id = ?
    """, (candidate_id,))

    connection.commit()
    connection.close()

    print("\n새 전략 버전 생성 완료")
    print(f"후보 ID: {candidate_id}")
    print(f"기반 버전: {base_version}")
    print(f"새 버전: {new_version}")
    print("상태 변경: approved → version_created")

    return True