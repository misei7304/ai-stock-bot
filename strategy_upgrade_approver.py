from database import get_connection


def approve_strategy_upgrade_candidate(candidate_id):
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

    row = cursor.fetchone()

    if row is None:
        print("해당 후보를 찾을 수 없습니다.")
        connection.close()
        return

    candidate_id, base_version, suggestion_text, status = row

    if status != "reviewed":
        print("reviewed 상태인 후보만 승인 가능합니다.")
        connection.close()
        return

    cursor.execute("""
        UPDATE strategy_upgrade_candidates
        SET status = 'approved'
        WHERE id = ?
    """, (candidate_id,))

    connection.commit()
    connection.close()

    print("\n전략 업그레이드 승인 완료")
    print(f"후보 ID: {candidate_id}")
    print(f"기반 버전: {base_version}")
    print("상태: approved")