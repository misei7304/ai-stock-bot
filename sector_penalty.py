from database import get_connection


def get_sector_penalty(sector_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND r.sector_name = ?
    """, (sector_name,))

    rows = cursor.fetchall()
    connection.close()

    if len(rows) < 3:
        return 0

    returns = [row[0] for row in rows]
    average_return = sum(returns) / len(returns)

    if average_return < -2:
        return -5
    elif average_return < 0:
        return -2
    else:
        return 0


def apply_sector_penalty(stock):
    sector_penalty = get_sector_penalty(stock["sector_name"])

    stock["sector_penalty"] = sector_penalty
    stock["final_score"] = stock["final_score"] + sector_penalty

    return stock