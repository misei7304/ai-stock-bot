from storage.database import get_connection


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

    if not rows:
        print("등록된 전략 버전이 없습니다.")
        return

    for version, name, is_active, created_at in rows:
        status = "ACTIVE" if is_active else ""

        print(
            f"{version} | "
            f"{name} | "
            f"{status} | "
            f"{created_at}"
        )


def main():
    list_strategy_versions()


if __name__ == "__main__":
    main()