from database import get_connection


def analyze_score_adjustments():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            r.adaptive_bonus,
            r.sector_penalty,
            r.factor_penalty,
            p.current_return
        FROM recommendation_performance p
        JOIN recommendations r
        ON p.recommendation_id = r.id
        WHERE p.current_return IS NOT NULL
    """)

    rows = cursor.fetchall()
    connection.close()

    print("\n" + "#" * 80)
    print("점수 조정 효과 분석")
    print("#" * 80)

    if len(rows) == 0:
        print("분석 가능한 점수 조정 데이터가 없습니다.")
        return

    adaptive_stats = {}
    sector_penalty_stats = {}
    factor_penalty_stats = {}

    for adaptive_bonus, sector_penalty, factor_penalty, current_return in rows:
        if adaptive_bonus is None:
            adaptive_bonus = 0

        if sector_penalty is None:
            sector_penalty = 0

        if factor_penalty is None:
            factor_penalty = 0

        if adaptive_bonus not in adaptive_stats:
            adaptive_stats[adaptive_bonus] = []
        adaptive_stats[adaptive_bonus].append(current_return)

        if sector_penalty not in sector_penalty_stats:
            sector_penalty_stats[sector_penalty] = []
        sector_penalty_stats[sector_penalty].append(current_return)

        if factor_penalty not in factor_penalty_stats:
            factor_penalty_stats[factor_penalty] = []
        factor_penalty_stats[factor_penalty].append(current_return)

    print("\n적응 보너스별 성과")
    for bonus, returns in adaptive_stats.items():
        average_return = sum(returns) / len(returns)
        print(
            f"적응보너스 {bonus} | "
            f"추천수 {len(returns)}회 | "
            f"평균수익률 {average_return:.2f}%"
        )

    print("\n섹터 패널티별 성과")
    for penalty, returns in sector_penalty_stats.items():
        average_return = sum(returns) / len(returns)
        print(
            f"섹터패널티 {penalty} | "
            f"추천수 {len(returns)}회 | "
            f"평균수익률 {average_return:.2f}%"
        )

    print("\n팩터 패널티별 성과")
    for penalty, returns in factor_penalty_stats.items():
        average_return = sum(returns) / len(returns)
        print(
            f"팩터패널티 {penalty} | "
            f"추천수 {len(returns)}회 | "
            f"평균수익률 {average_return:.2f}%"
        )