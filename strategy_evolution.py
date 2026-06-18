from datetime import date

from database import get_connection
from strategy_optimizer import get_strategy_optimization_suggestions


def save_strategy_evolution():
    suggestions = get_strategy_optimization_suggestions()
    suggestion_text = "\n".join(suggestions)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_evolution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evolution_date TEXT NOT NULL,
            suggestion_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    today = date.today().isoformat()

    cursor.execute("""
        SELECT COUNT(*)
        FROM strategy_evolution
        WHERE evolution_date = ?
        AND suggestion_text = ?
    """, (
        today,
        suggestion_text,
    ))

    existing_count = cursor.fetchone()[0]

    if existing_count > 0:
        connection.close()
        print("전략 개선 제안 저장 생략: 오늘 이미 같은 제안이 있습니다.")
        return False

    cursor.execute("""
        INSERT INTO strategy_evolution (
            evolution_date,
            suggestion_text
        )
        VALUES (?, ?)
    """, (
        today,
        suggestion_text,
    ))

    connection.commit()
    connection.close()

    print("전략 개선 제안 DB 저장 완료")
    return True