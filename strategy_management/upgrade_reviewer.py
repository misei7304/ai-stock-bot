from storage.database import get_connection


def review_strategy_upgrade_candidates():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            base_version,
            suggestion_text,
            status,
            created_at
        FROM strategy_upgrade_candidates
        WHERE status = 'pending'
        ORDER BY created_at ASC
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("전략 업그레이드 후보 검토")
    print("#" * 80)

    if len(rows) == 0:
        print("검토할 pending 후보가 없습니다.")
        connection.close()
        return

    for row in rows:
        candidate_id, base_version, suggestion_text, status, created_at = row

        print("\n" + "-" * 80)
        print(f"후보 ID: {candidate_id}")
        print(f"기반 버전: {base_version}")
        print(f"상태: {status}")
        print(f"생성시각: {created_at}")
        print("\n제안 내용:")
        print(suggestion_text)

        cursor.execute("""
            UPDATE strategy_upgrade_candidates
            SET status = 'reviewed'
            WHERE id = ?
        """, (candidate_id,))

        print("\n상태 변경: pending → reviewed")

    connection.commit()
    connection.close()

    print("\n모든 pending 후보 검토 완료")