import argparse

from strategy_management.version_activator import activate_strategy_version


def parse_args():
    parser = argparse.ArgumentParser(
        description="지정한 전략 버전을 활성화합니다."
    )
    parser.add_argument(
        "version",
        help="활성화할 전략 버전. 예: v1.2.0",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    success = activate_strategy_version(args.version)

    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()