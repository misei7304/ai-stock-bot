import argparse

from strategy_management.upgrade_candidate import (
    approve_strategy_candidate,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="검토 완료된 전략 업그레이드 후보를 승인합니다."
    )
    parser.add_argument(
        "candidate_id",
        type=int,
        help="승인할 전략 후보 ID",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    success = approve_strategy_candidate(
        args.candidate_id
    )

    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()