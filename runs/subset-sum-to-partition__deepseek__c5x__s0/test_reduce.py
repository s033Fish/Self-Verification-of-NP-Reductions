"""Test the reduction from Subset Sum to Partition.

The script generates a number of small random instances, checks that the
reduction preserves the answer, and writes a verdict file.
"""

from __future__ import annotations
import random
import json
import sys

import problems
from reduce import reduce as reduce_instance
from solve_bruteforce import subset_sum_bruteforce, partition_bruteforce


def run_tests(num_tests: int = 2000) -> dict:
    passed = 0
    for _ in range(num_tests):
        # random length 0..6
        n = random.randint(0, 6)
        numbers = [random.randint(0, 5) for _ in range(n)]
        total = sum(numbers)
        # target range -2 .. total+2
        target = random.randint(-2, total + 2)
        src = {"numbers": numbers, "target": target}
        # validate source
        try:
            problems.SubsetSum.validate(src)
        except Exception as e:
            print("Invalid source instance", src, e)
            continue
        # compute source answer
        src_ans = subset_sum_bruteforce(src)
        # reduce
        tgt = reduce_instance(src)
        # validate target
        try:
            problems.Partition.validate(tgt)
        except Exception as e:
            print("Invalid target produced", tgt, e)
            return {"verified": False, "tests_run": passed, "tests_passed": passed}
        tgt_ans = partition_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            # discrepancy
            print("Discrepancy found", src, src_ans, tgt, tgt_ans)
            return {"verified": False, "tests_run": passed + 1, "tests_passed": passed}
    return {"verified": True, "tests_run": num_tests, "tests_passed": passed}

if __name__ == "__main__":
    result = run_tests()
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    # also print for visibility
    print(json.dumps(result))
    sys.exit(0 if result["verified"] else 1)
