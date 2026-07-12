import sys

from strategy_management.upgrade_candidate import (
    approve_strategy_candidate
)


if len(sys.argv) < 2:
    print("사용법: python approve_candidate.py 후보ID")
    sys.exit(1)

candidate_id = int(sys.argv[1])

approve_strategy_candidate(candidate_id)