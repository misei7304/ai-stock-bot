from strategy_version_performance import (
    get_strategy_version_performance_data
)


def get_strategy_version_comparison_summary():
    versions = get_strategy_version_performance_data()

    summary = []

    if len(versions) < 2:
        summary.append("비교 가능한 전략 버전이 부족합니다.")
        return summary

    current_version = versions[0]
    previous_version = versions[1]

    return_diff = (
        current_version["average_return"]
        - previous_version["average_return"]
    )

    summary.append(f"현재 버전: {current_version['version']}")
    summary.append(f"비교 대상: {previous_version['version']}")
    summary.append(
        f"평균수익률 변화: "
        f"{previous_version['average_return']:.2f}% "
        f"→ "
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