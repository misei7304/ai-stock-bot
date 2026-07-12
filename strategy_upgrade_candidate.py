from storage.database import get_connection
from strategy_version import get_current_strategy_version
from performance_analysis.strategy_optimizer import get_strategy_optimization_suggestions


def save_strategy_upgrade_candidate():
    current_version = get_current_strategy_version()
    suggestions = get_strategy_optimization_suggestions()
    suggestion_text = "\n".join(suggestions)

    if "손실 데이터가 아직 부족합니다." in suggestion_text:
        print("전략 업그레이드 후보 저장 생략: 손실 데이터가 아직 부족합니다.")
        return False

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

def get_pending_strategy_candidates():
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
        SELECT
            id,
            base_version,
            suggestion_text,
            status,
            created_at
        FROM strategy_upgrade_candidates
        WHERE status = 'pending'
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    candidates = []

    for row in rows:
        candidates.append({
            "id": row[0],
            "base_version": row[1],
            "suggestion": row[2],
            "status": row[3],
            "created_at": row[4],
        })

    return candidates

def mark_strategy_candidate_reviewed(candidate_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE strategy_upgrade_candidates
        SET status = 'reviewed'
        WHERE id = ?
        AND status = 'pending'
    """, (
        candidate_id,
    ))

    updated_count = cursor.rowcount

    connection.commit()
    connection.close()

    if updated_count == 0:
        print(f"후보 검토 처리 실패: ID {candidate_id}")
        return False

    print(f"후보 검토 완료: ID {candidate_id}")
    return True

def approve_strategy_candidate(candidate_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE strategy_upgrade_candidates
        SET status = 'approved'
        WHERE id = ?
        AND status = 'reviewed'
    """, (
        candidate_id,
    ))

    updated_count = cursor.rowcount

    connection.commit()
    connection.close()

    if updated_count == 0:
        print(f"후보 승인 실패: ID {candidate_id}")
        return False

    print(f"후보 승인 완료: ID {candidate_id}")
    return True