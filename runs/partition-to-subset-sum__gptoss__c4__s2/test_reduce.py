import itertools
import json
import sys
from typing import List, Dict, Any

from reduce import reduce as reduction
from solve_partition import partition_yes
from solve_subset_sum import subset_sum_yes


def generate_instances(max_len: int = 6, max_val: int = 5) -> List[Dict[str, Any]]:
    instances = []
    for length in range(max_len + 1):
        for combo in itertools.product(range(max_val + 1), repeat=length):
            instances.append({"numbers": list(combo)})
    return instances


def main():
    instances = generate_instances()
    total = len(instances)
    passed = 0
    for inst in instances:
        # compute answers
        ans_part = partition_yes(inst)
        reduced = reduction(inst)
        ans_sub = subset_sum_yes(reduced)
        if ans_part == ans_sub:
            passed += 1
        else:
            print("Mismatch!", inst, "reduced", reduced, "partition", ans_part, "subset", ans_sub)
            # exit early for debugging
            sys.exit(1)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
