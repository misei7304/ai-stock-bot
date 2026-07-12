from storage.database import get_connection
from strategy_version import get_current_strategy_version
from performance_analysis.strategy_version_performance import get_strategy_version_performance_data


def get_previous_strategy_version(current_version):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM strategy_versions
        WHERE version = ?
    """, (current_version,))

    row = cursor.fetchone()

    if row is None:
        connection.close()
        return None

    current_id = row[0]

    cursor.execute("""
        SELECT version
        FROM strategy_versions
        WHERE id < ?
        ORDER BY id DESC
        LIMIT 1
    """, (current_id,))

    previous = cursor.fetchone()
    connection.close()

    if previous is None:
        return None

    return previous[0]


def find_performance(version, performance_data):
    for item in performance_data:
        if item["version"] == version:
            return item

    return {
        "version": version,
        "recommendation_count": 0,
        "success_rate": 0,
        "average_return": 0,
        "best_return": 0,
        "worst_return": 0,
    }


def get_strategy_version_comparison_summary():
    performance_data = get_strategy_version_performance_data()

    summary = []

    current_version_name = get_current_strategy_version()
    previous_version_name = get_previous_strategy_version(current_version_name)

    if previous_version_name is None:
        summary.append("비교 가능한 이전 전략 버전이 없습니다.")
        return summary

    current_version = find_performance(current_version_name, performance_data)
    previous_version = find_performance(previous_version_name, performance_data)

    return_diff = current_version["average_return"] - previous_version["average_return"]

    summary.append(f"현재 버전: {current_version['version']}")
    summary.append(f"비교 대상: {previous_version['version']}")
    summary.append(
        f"평균수익률 변화: "
        f"{previous_version['average_return']:.2f}% → "
        f"{current_version['average_return']:.2f}%"
    )
    summary.append(f"개선폭: {return_diff:+.2f}%")

    if return_diff > 0:
        summary.append("판단: 현재 버전이 더 우수")
    elif return_diff < 0:
        summary.append("판단: 이전 버전이 더 우수")
    else:
        summary.append("판단: 차이 없음")

    total_count = (
        current_version["recommendation_count"]
        + previous_version["recommendation_count"]
    )

    if total_count < 20:
        summary.append("신뢰도: 낮음 (추천수 부족)")
    elif total_count < 100:
        summary.append("신뢰도: 보통")
    else:
        summary.append("신뢰도: 높음")

    return summary


def analyze_strategy_version_comparison():
    print("\n" + "#" * 80)
    print("전략 버전 비교")
    print("#" * 80)

    summary = get_strategy_version_comparison_summary()

    for line in summary:
        print(line)