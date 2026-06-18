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


def get_macd_bucket(macd, macd_signal):
    macd_gap = macd - macd_signal

    if macd_gap <= 0:
        return "MACD <= Signal"
    elif macd_gap < 500:
        return "0~500"
    elif macd_gap < 1000:
        return "500~1000"
    elif macd_gap < 2000:
        return "1000~2000"
    else:
        return "2000+"


def analyze_macd_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.macd,
            r.macd_signal,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND r.macd IS NOT NULL
        AND r.macd_signal IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("MACD 구간별 실전 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 MACD 실전 성과 데이터가 없습니다.")
        connection.close()
        return

    bucket_stats = {}

    for macd, macd_signal, current_return in rows:
        bucket = get_macd_bucket(macd, macd_signal)

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
        "MACD <= Signal": 1,
        "0~500": 2,
        "500~1000": 3,
        "1000~2000": 4,
        "2000+": 5,
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

def get_atr_percent_bucket(atr_percent):
    if atr_percent < 2:
        return "0~2%"
    elif atr_percent < 4:
        return "2~4%"
    elif atr_percent < 6:
        return "4~6%"
    elif atr_percent < 8:
        return "6~8%"
    else:
        return "8%+"


def analyze_atr_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.atr_percent,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND r.atr_percent IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("ATR% 구간별 실전 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 ATR% 실전 성과 데이터가 없습니다.")
        connection.close()
        return

    bucket_stats = {}

    for atr_percent, current_return in rows:
        bucket = get_atr_percent_bucket(atr_percent)

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
        "0~2%": 1,
        "2~4%": 2,
        "4~6%": 3,
        "6~8%": 4,
        "8%+": 5,
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

def analyze_bollinger_performance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.bollinger_score,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
        AND r.bollinger_score IS NOT NULL
    """)

    rows = cursor.fetchall()

    print("\n" + "#" * 80)
    print("볼린저 점수별 실전 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 볼린저 실전 성과 데이터가 없습니다.")
        connection.close()
        return

    score_stats = {}

    for bollinger_score, current_return in rows:
        if bollinger_score not in score_stats:
            score_stats[bollinger_score] = []

        score_stats[bollinger_score].append(current_return)

    score_results = []

    for bollinger_score, returns in score_stats.items():
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

        score_results.append({
            "bollinger_score": bollinger_score,
            "total_count": total_count,
            "win_count": win_count,
            "loss_count": loss_count,
            "success_rate": success_rate,
            "average_return": average_return,
            "best_return": best_return,
            "worst_return": worst_return,
        })

    score_results = sorted(
        score_results,
        key=lambda x: x["bollinger_score"],
        reverse=True
    )

    for result in score_results:
        print(
            f"볼린저점수 {result['bollinger_score']} | "
            f"추천수 {result['total_count']}회 | "
            f"수익중 {result['win_count']}회 | "
            f"손실/보합 {result['loss_count']}회 | "
            f"성공률 {result['success_rate']:.2f}% | "
            f"평균수익률 {result['average_return']:.2f}% | "
            f"최고수익률 {result['best_return']:.2f}% | "
            f"최저수익률 {result['worst_return']:.2f}%"
        )

    connection.close()

def get_final_score_bucket(final_score):
    if final_score < 0:
        return "0점 미만"
    elif final_score < 30:
        return "0~30"
    elif final_score < 50:
        return "30~50"
    elif final_score < 70:
        return "50~70"
    elif final_score < 100:
        return "70~100"
    else:
        return "100+"


def analyze_final_score_performance():
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

    print("\n" + "#" * 80)
    print("최종점수 구간별 실전 성과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 최종점수 실전 성과 데이터가 없습니다.")
        connection.close()
        return

    bucket_stats = {}

    for final_score, current_return in rows:
        bucket = get_final_score_bucket(final_score)

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
        "0점 미만": 1,
        "0~30": 2,
        "30~50": 3,
        "50~70": 4,
        "70~100": 5,
        "100+": 6,
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