import pandas as pd

sector_map = {
    "삼성전자": "반도체",
    "SK하이닉스": "반도체",
    "삼성전기": "전자부품",

    "NAVER": "인터넷",
    "카카오": "인터넷",

    "LG화학": "화학",
    "롯데케미칼": "화학",

    "삼성SDI": "배터리",
    "LG에너지솔루션": "배터리",

    "현대차": "자동차",
    "기아": "자동차",
    "현대모비스": "자동차부품",
    "한국타이어앤테크놀로지": "자동차부품",
    "현대글로비스": "물류",

    "셀트리온": "바이오",
    "삼성바이오로직스": "바이오",

    "POSCO홀딩스": "철강",
    "현대제철": "철강",
    "고려아연": "비철금속",

    "신한지주": "금융",
    "하나금융지주": "금융",
    "KB금융": "금융",
    "우리금융지주": "금융",
    "기업은행": "금융",
    "한국금융지주": "증권",
    "미래에셋증권": "증권",
    "삼성생명": "보험",

    "삼성물산": "지주/상사",
    "LG": "지주/상사",
    "SK": "지주/상사",
    "포스코인터내셔널": "상사",

    "두산에너빌리티": "전력기기",
    "LS ELECTRIC": "전력기기",
    "HD현대일렉트릭": "전력기기",
    "한국전력": "전력",

    "한화오션": "조선",
    "HD현대중공업": "조선",
    "삼성중공업": "조선",
    "HD한국조선해양": "조선",

    "SK이노베이션": "에너지",
    "S-Oil": "에너지",

    "SK텔레콤": "통신",
    "KT": "통신",

    "KT&G": "필수소비재",
    "아모레퍼시픽": "화장품",

    "HMM": "해운",

    "LG전자": "전자",
    "삼성에스디에스": "IT서비스",

    "넷마블": "게임",
    "크래프톤": "게임",
}

def get_sector_name(company_name):
    return sector_map.get(company_name, "기타")


MIN_SECTOR_STOCK_COUNT_FOR_BONUS = 2


def calculate_sector_bonus(sector_name, sector_ranking):
    eligible_sectors = [
        sector
        for sector in sector_ranking
        if sector["count"] >= MIN_SECTOR_STOCK_COUNT_FOR_BONUS
    ]

    for index, sector in enumerate(eligible_sectors):
        if sector["sector_name"] != sector_name:
            continue

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
        if pd.isna(stock["final_score"]):
            continue

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

    if len(sector_ranking) == 0:
        print("분석 가능한 섹터 데이터가 없습니다.")
        return

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