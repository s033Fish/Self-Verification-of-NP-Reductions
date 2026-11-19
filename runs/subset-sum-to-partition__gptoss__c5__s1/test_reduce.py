"""Tests for the reduction from Subset Sum to Partition.

The repository provides only validation functions for the two problems.  To
verify the correctness of ``reduce.py`` we implement straightforward brute‑
force solvers for both problems and compare the answer of a source instance
with the answer of the reduced target instance.

The test suite generates a variety of small random instances (including edge
cases) and checks that the reduction preserves the yes/no answer.  It also
ensures that ``reduce`` returns a valid Partition instance.

The script prints a JSON object ``verdict.json`` as required by the task
description.  ``verdict.json`` contains the fields ``verified`` (true iff all
tests passed), ``tests_run`` and ``tests_passed``.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Dict

from problems import SubsetSum, Partition
from reduce import reduce as reduce_instance


def subset_sum_bruteforce(numbers: List[int], target: int) -> bool:
    """Return True iff a subset of ``numbers`` sums exactly to ``target``.

    The implementation is exponential but the test suite only uses tiny
    inputs (len <= 12) so it is fast enough.
    """
    n = len(numbers)
    # Early handling of the edge cases defined in the problem statement.
    if target == 0:
        return True
    if target < 0:
        return False
    # Enumerate all subsets via bitmask.
    for mask in range(1, 1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def partition_bruteforce(numbers: List[int]) -> bool:
    """Return True iff ``numbers`` can be split into two groups with equal sum.
    """
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    # Subset sum to half is sufficient.
    return subset_sum_bruteforce(numbers, half)


def generate_random_instance(max_len: int = 8, max_val: int = 5) -> Dict:
    """Generate a random Subset Sum instance.

    The target may be outside the achievable range to test the "obviously no"
    branch of the reduction.
    """
    length = random.randint(0, max_len)
    numbers = [random.randint(0, max_val) for _ in range(length)]
    total = sum(numbers)
    # Choose target in a range that includes values below 0 and above total.
    target = random.randint(-max_val, total + max_val)
    return {"numbers": numbers, "target": target}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    # Include some deterministic edge cases.
    edge_cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 1, 2], "target": 3},
        {"numbers": [5, 5, 5], "target": 10},
    ]
    instances = edge_cases + [generate_random_instance() for _ in range(200)]

    for instance in instances:
        tests_run += 1
        # Validate source instance (should never raise).
        SubsetSum.validate(instance)
        source_answer = subset_sum_bruteforce(instance["numbers"], instance["target"])
        # Reduce and validate target instance.
        reduced = reduce_instance(instance)
        Partition.validate(reduced)
        target_answer = partition_bruteforce(reduced["numbers"])
        if source_answer == target_answer:
            tests_passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Source:", instance, "Answer:", source_answer, file=sys.stderr)
            print("Reduced:", reduced, "Answer:", target_answer, file=sys.stderr)
    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    # Also print to stdout for visibility.
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
