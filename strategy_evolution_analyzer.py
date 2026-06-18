from database import get_connection


def analyze_strategy_evolution_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            evolution_date,
            suggestion_text,
            created_at
        FROM strategy_evolution
        ORDER BY created_at DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    connection.close()

    print("\n" + "#" * 80)
    print("전략 개선 이력 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("저장된 전략 개선 이력이 없습니다.")
        return

    print(f"총 최근 전략 개선 기록: {len(rows)}개")

    for row in rows:
        evolution_date, suggestion_text, created_at = row

        print("\n" + "-" * 80)
        print(f"날짜: {evolution_date}")
        print(f"저장시각: {created_at}")
        print("\n제안 내용:")
        print(suggestion_text)