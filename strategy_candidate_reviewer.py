from strategy_upgrade_candidate import (
    get_pending_strategy_candidates
)


def review_strategy_candidates():
    candidates = get_pending_strategy_candidates()

    print("\n" + "#" * 80)
    print("전략 후보 검토")
    print("#" * 80)

    if len(candidates) == 0:
        print("검토할 후보가 없습니다.")
        return

    for candidate in candidates:
        print("-" * 80)
        print(f"후보 ID: {candidate['id']}")
        print(f"기반 버전: {candidate['base_version']}")
        print(f"상태: {candidate['status']}")
        print()
        print(candidate["suggestion"])