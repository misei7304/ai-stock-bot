import argparse

from strategy_management.upgrade_candidate import (
    mark_strategy_candidate_reviewed,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="전략 업그레이드 후보를 검토 완료 상태로 변경합니다."
    )
    parser.add_argument(
        "candidate_id",
        type=int,
        help="검토 처리할 전략 후보 ID",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    success = mark_strategy_candidate_reviewed(
        args.candidate_id
    )

    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()