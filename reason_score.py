from database import get_connection
from recommendation_reason import generate_recommendation_reason


def get_reason_score_adjustment(stock, market_result):
    recommendation_reason = generate_recommendation_reason(stock, market_result)
    reasons = recommendation_reason.split(". ")

    connection = get_connection()
    cursor = connection.cursor()

    adjustment = 0

    for reason in reasons:
        reason = reason.strip()

        if reason == "":
            continue

        cursor.execute("""
            SELECT p.current_return
            FROM recommendation_performance p
            JOIN recommendations r
            ON p.recommendation_id = r.id
            WHERE p.current_return IS NOT NULL
            AND r.recommendation_reason LIKE ?
        """, (f"%{reason}%",))

        rows = cursor.fetchall()

        if len(rows) < 3:
            continue

        returns = [row[0] for row in rows]
        average_return = sum(returns) / len(returns)

        if average_return > 2:
            adjustment += 2
        elif average_return < -2:
            adjustment -= 2

    connection.close()

    return adjustment


def apply_reason_score(stock, market_result):
    reason_score = get_reason_score_adjustment(stock, market_result)

    stock["reason_score"] = reason_score
    stock["final_score"] = stock["final_score"] + reason_score

    return stock