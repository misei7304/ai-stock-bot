import sys

from strategy_management.upgrade_candidate import mark_strategy_candidate_reviewed


if len(sys.argv) < 2:
    print("사용법: python review_candidate.py 후보ID")
    sys.exit(1)

candidate_id = int(sys.argv[1])

mark_strategy_candidate_reviewed(candidate_id)