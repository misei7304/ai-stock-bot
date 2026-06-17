sector_map = {
    "삼성전자": "반도체",
    "SK하이닉스": "반도체",

    "현대차": "자동차",
    "현대모비스": "자동차",

    "LG에너지솔루션": "배터리",
    "삼성SDI": "배터리",

    "LG화학": "화학",

    "NAVER": "인터넷",
    "카카오": "인터넷",

    "삼성바이오로직스": "바이오",
    "셀트리온": "바이오",

    "POSCO홀딩스": "철강",

    "삼성물산": "지주/상사",

    "신한지주": "금융",
    "하나금융지주": "금융",
}

def get_sector_name(company_name):
    return sector_map.get(company_name, "기타")


def calculate_sector_bonus(sector_name, sector_ranking):

    for index, sector in enumerate(sector_ranking):

        if sector["sector_name"] == sector_name:

            if index == 0:
                return 5

            if index == 1:
                return 3

            if index == 2:
                return 2

            return 0

    return 0


def analyze_sector_performance(results):

    sector_stats = {}

    for stock in results:
        company_name = stock["company_name"]
        sector_name = sector_map.get(company_name, "기타")

        if sector_name not in sector_stats:
            sector_stats[sector_name] = {
                "count": 0,
                "total_final_score": 0,
                "total_average_return": 0,
                "total_win_rate": 0,
                "buy_candidate_count": 0,
            }

        sector_stats[sector_name]["count"] += 1
        sector_stats[sector_name]["total_final_score"] += stock["final_score"]
        sector_stats[sector_name]["total_average_return"] += stock["average_return"]
        sector_stats[sector_name]["total_win_rate"] += stock["win_rate"]

        if stock["is_buy_candidate"]:
            sector_stats[sector_name]["buy_candidate_count"] += 1

    sector_ranking = []

    for sector_name, stats in sector_stats.items():

        count = stats["count"]

        average_final_score = stats["total_final_score"] / count
        average_return = stats["total_average_return"] / count
        average_win_rate = stats["total_win_rate"] / count

        sector_ranking.append({
            "sector_name": sector_name,
            "count": count,
            "average_final_score": average_final_score,
            "average_return": average_return,
            "average_win_rate": average_win_rate,
            "buy_candidate_count": stats["buy_candidate_count"],
        })

    sector_ranking = sorted(
        sector_ranking,
        key=lambda x: x["average_final_score"],
        reverse=True
    )

    return sector_ranking


def print_sector_performance(results):

    sector_ranking = analyze_sector_performance(results)

    print("\n" + "#" * 80)
    print("섹터별 성과 분석")
    print("#" * 80)

    rank = 1

    for sector in sector_ranking:
        print(
            f"{rank}위 | "
            f"{sector['sector_name']} | "
            f"종목수 {sector['count']}개 | "
            f"평균최종점수 {sector['average_final_score']:.2f} | "
            f"평균수익 {sector['average_return']:.2f}% | "
            f"평균승률 {sector['average_win_rate']:.2f}% | "
            f"매수후보 {sector['buy_candidate_count']}개"
        )

        rank += 1