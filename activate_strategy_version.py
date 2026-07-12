import sys

from storage.database import get_connection


def activate_strategy_version(version):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM strategy_versions
        WHERE version = ?
    """, (version,))

    exists = cursor.fetchone()[0]

    if exists == 0:
        connection.close()
        print(f"전략 활성화 실패: 존재하지 않는 버전입니다. {version}")
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

    print(f"전략 활성화 완료: {version}")
    return True


if len(sys.argv) < 2:
    print("사용법: python activate_strategy_version.py 버전")
    sys.exit(1)

version = sys.argv[1]

activate_strategy_version(version)