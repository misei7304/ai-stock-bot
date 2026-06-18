from database import get_connection


def get_rsi_bucket(rsi):
    if rsi < 30:
        return "0~30"
    elif rsi < 40:
        return "30~40"
    elif rsi < 50:
        return "40~50"
    elif rsi < 60:
        return "50~60"
    elif rsi < 70:
        return "60~70"
    else:
        return "70+"


def analyze_rsi_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.rsi,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND r.rsi IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("RSI 구간별 실전 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 RSI 실전 성과 데이터가 없습니다.")
        connection.close()
        return

    bucket_stats = {}

    for rsi, current_return in rows:
        bucket = get_rsi_bucket(rsi)

        if bucket not in bucket_stats:
            bucket_stats[bucket] = []

        bucket_stats[bucket].append(current_return)

    bucket_results = []

    for bucket, returns in bucket_stats.items():
        total_count = len(returns)
        win_count = 0

        for current_return in returns:
            if current_return > 0:
                win_count += 1

        loss_count = total_count - win_count
        success_rate = (win_count / total_count) * 100
        average_return = sum(returns) / total_count
        best_return = max(returns)
        worst_return = min(returns)

        bucket_results.append({
            "bucket": bucket,
            "total_count": total_count,
            "win_count": win_count,
            "loss_count": loss_count,
            "success_rate": success_rate,
            "average_return": average_return,
            "best_return": best_return,
            "worst_return": worst_return,
        })

    bucket_order = {
        "0~30": 1,
        "30~40": 2,
        "40~50": 3,
        "50~60": 4,
        "60~70": 5,
        "70+": 6,
    }

    bucket_results = sorted(
        bucket_results,
        key=lambda x: bucket_order[x["bucket"]]
    )

    for result in bucket_results:
        print(
            f"{result['bucket']} | "
            f"추천수 {result['total_count']}회 | "
            f"수익중 {result['win_count']}회 | "
            f"손실/보합 {result['loss_count']}회 | "
            f"성공률 {result['success_rate']:.2f}% | "
            f"평균수익률 {result['average_return']:.2f}% | "
            f"최고수익률 {result['best_return']:.2f}% | "
            f"최저수익률 {result['worst_return']:.2f}%"
        )

    connection.close()