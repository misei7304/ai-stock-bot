from database import get_connection


def list_strategy_versions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            version,
            name,
            is_active,
            created_at
        FROM strategy_versions
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    print("\n" + "#" * 80)
    print("전략 버전 목록")
    print("#" * 80)

    for row in rows:
        version = row[0]
        name = row[1]
        is_active = row[2]
        created_at = row[3]

        status = "ACTIVE" if is_active else ""

        print(
            f"{version} | "
            f"{name} | "
            f"{status} | "
            f"{created_at}"
        )


list_strategy_versions()