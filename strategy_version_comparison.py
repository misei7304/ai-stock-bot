from strategy_version_performance import (
    get_strategy_version_performance_data
)


def analyze_strategy_version_comparison():
    versions = get_strategy_version_performance_data()

    if len(versions) < 2:
        print("비교 가능한 전략 버전이 부족합니다.")
        return

    current_version = versions[0]
    previous_version = versions[1]

    print("\n" + "#" * 80)
    print("전략 버전 비교")
    print("#" * 80)

    print(f"현재 버전: {current_version['version']}")
    print(f"비교 대상: {previous_version['version']}")

    return_diff = (
        current_version["average_return"]
        - previous_version["average_return"]
    )

    print()
    print(
        f"평균수익률 변화: "
        f"{previous_version['average_return']:.2f}% "
        f"→ "
        f"{current_version['average_return']:.2f}%"
    )

    print(f"개선폭: {return_diff:+.2f}%")

    if return_diff > 0:
        print("판단: 현재 버전이 더 우수")
    elif return_diff < 0:
        print("판단: 이전 버전이 더 우수")
    else:
        print("판단: 차이 없음")

    total_count = (
        current_version["recommendation_count"]
        + previous_version["recommendation_count"]
    )

    if total_count < 20:
        print("신뢰도: 낮음 (추천수 부족)")
    elif total_count < 100:
        print("신뢰도: 보통")
    else:
        print("신뢰도: 높음")