from strategy_version_performance import (
    get_strategy_version_performance_data
)


def get_strategy_rollback_analysis_summary():
    versions = get_strategy_version_performance_data()

    summary = []

    if len(versions) < 2:
        summary.append("롤백 판단 불가: 비교 가능한 전략 버전이 부족합니다.")
        return summary

    current_version = versions[0]
    previous_version = versions[1]

    total_count = (
        current_version["recommendation_count"]
        + previous_version["recommendation_count"]
    )

    return_diff = (
        current_version["average_return"]
        - previous_version["average_return"]
    )

    summary.append(f"현재 전략 버전: {current_version['version']}")
    summary.append(f"이전 전략 버전: {previous_version['version']}")
    summary.append(f"현재 버전 평균수익률: {current_version['average_return']:.2f}%")
    summary.append(f"이전 버전 평균수익률: {previous_version['average_return']:.2f}%")
    summary.append(f"수익률 차이: {return_diff:+.2f}%")
    summary.append(f"비교 추천수 합계: {total_count}회")

    if total_count < 20:
        summary.append("롤백 판단: 보류")
        summary.append("이유: 추천수가 20회 미만이라 통계 신뢰도가 낮습니다.")
        return summary

    if return_diff < -2:
        summary.append("롤백 판단: 롤백 검토 필요")
        summary.append("이유: 현재 전략이 이전 전략보다 평균수익률이 2%p 이상 낮습니다.")
    elif return_diff < 0:
        summary.append("롤백 판단: 주의")
        summary.append("이유: 현재 전략이 이전 전략보다 낮지만 차이가 크지 않습니다.")
    else:
        summary.append("롤백 판단: 유지")
        summary.append("이유: 현재 전략이 이전 전략보다 같거나 더 좋습니다.")

    return summary


def analyze_strategy_rollback():
    print("\n" + "#" * 80)
    print("전략 롤백 판단")
    print("#" * 80)

    summary = get_strategy_rollback_analysis_summary()

    for line in summary:
        print(line)