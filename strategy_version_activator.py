from database import get_connection


def activate_strategy_version(version):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, version, name
        FROM strategy_versions
        WHERE version = ?
    """, (version,))

    row = cursor.fetchone()

    if row is None:
        print("해당 전략 버전을 찾을 수 없습니다.")
        connection.close()
        return False

    cursor.execute("""
        UPDATE strategy_versions
        SET is_active = 0
    """)

    cursor.execute("""
        UPDATE strategy_versions
        SET is_active = 1
        WHERE version = ?
    """, (version,))

    connection.commit()
    connection.close()

    print("\n전략 버전 활성화 완료")
    print(f"활성 버전: {version}")

    return True