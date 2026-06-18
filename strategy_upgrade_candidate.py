from database import get_connection
from strategy_version import get_current_strategy_version
from strategy_optimizer import get_strategy_optimization_suggestions


def save_strategy_upgrade_candidate():
    current_version = get_current_strategy_version()
    suggestions = get_strategy_optimization_suggestions()
    suggestion_text = "\n".join(suggestions)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_upgrade_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_version TEXT NOT NULL,
            suggestion_text TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        SELECT COUNT(*)
        FROM strategy_upgrade_candidates
        WHERE base_version = ?
        AND suggestion_text = ?
        AND status = 'pending'
    """, (
        current_version,
        suggestion_text,
    ))

    existing_count = cursor.fetchone()[0]

    if existing_count > 0:
        connection.close()
        print("전략 업그레이드 후보 저장 생략: 이미 같은 pending 후보가 있습니다.")
        return False

    cursor.execute("""
        INSERT INTO strategy_upgrade_candidates (
            base_version,
            suggestion_text,
            status
        )
        VALUES (?, ?, ?)
    """, (
        current_version,
        suggestion_text,
        "pending",
    ))

    connection.commit()
    connection.close()

    print("전략 업그레이드 후보 저장 완료")
    return True