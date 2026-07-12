from storage.database import get_connection


def get_average_return_by_final_score_bucket(final_score):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.final_score,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND r.final_score IS NOT NULL
    """)

    rows = cursor.fetchall()
    connection.close()

    if len(rows) < 5:
        return 0

    matching_returns = []

    for saved_final_score, current_return in rows:
        if final_score < 30 and saved_final_score < 30:
            matching_returns.append(current_return)
        elif final_score >= 30 and final_score < 50 and saved_final_score >= 30 and saved_final_score < 50:
            matching_returns.append(current_return)
        elif final_score >= 50 and final_score < 70 and saved_final_score >= 50 and saved_final_score < 70:
            matching_returns.append(current_return)
        elif final_score >= 70 and final_score < 100 and saved_final_score >= 70 and saved_final_score < 100:
            matching_returns.append(current_return)
        elif final_score >= 100 and saved_final_score >= 100:
            matching_returns.append(current_return)

    if len(matching_returns) == 0:
        return 0

    average_return = sum(matching_returns) / len(matching_returns)

    if average_return > 2:
        return 5
    elif average_return > 0:
        return 2
    elif average_return < -2:
        return -5
    elif average_return < 0:
        return -2
    else:
        return 0


def apply_adaptive_score(stock):
    adaptive_bonus = get_average_return_by_final_score_bucket(
        stock["final_score"]
    )

    stock["adaptive_bonus"] = adaptive_bonus
    stock["final_score"] = stock["final_score"] + adaptive_bonus

    return stock