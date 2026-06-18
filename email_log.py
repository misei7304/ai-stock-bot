from datetime import date

from database import get_connection


def was_email_sent_today():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sent_date TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    today = date.today().isoformat()

    cursor.execute("""
        SELECT id
        FROM email_logs
        WHERE sent_date = ?
    """, (today,))

    row = cursor.fetchone()

    connection.close()

    return row is not None


def mark_email_sent_today():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sent_date TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    today = date.today().isoformat()

    cursor.execute("""
        INSERT OR IGNORE INTO email_logs (sent_date)
        VALUES (?)
    """, (today,))

    connection.commit()
    connection.close()