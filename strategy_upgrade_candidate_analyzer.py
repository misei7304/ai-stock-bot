from database import get_connection


def analyze_strategy_upgrade_candidates():
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
        ORDER BY created_at DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    connection.close()

    print("\n" + "#" * 80)
    print("전략 업그레이드 후보 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("저장된 전략 업그레이드 후보가 없습니다.")
        return

    print(f"최근 전략 업그레이드 후보: {len(rows)}개")

    for row in rows:
        candidate_id, base_version, suggestion_text, status, created_at = row

        print("\n" + "-" * 80)
        print(f"후보 ID: {candidate_id}")
        print(f"기반 전략 버전: {base_version}")
        print(f"상태: {status}")
        print(f"생성시각: {created_at}")
        print("\n제안 내용:")
        print(suggestion_text)