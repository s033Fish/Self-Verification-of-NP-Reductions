"""Test suite for the reduction from Subset Sum to Partition.

The repository provides only validation functions for the two problems.
This file implements straightforward brute‑force solvers based on the
definitions in ``problems.py`` and checks that ``reduce.py`` preserves the
answer for a wide range of small instances.

If all generated instances pass, a ``verdict.json`` file is written with
the fields required by the task description.
"""

from __future__ import annotations

import itertools
import json
import random
from typing import List, Dict, Any

from problems import SubsetSum, Partition
from reduce import reduce as reduce_instance


def subset_sum_bruteforce(numbers: List[int], target: int) -> bool:
    """Return True iff a sub‑list of *numbers* sums to *target*.

    Implements the exact semantics from the docstring of ``SubsetSum``:
    * ``target == 0`` is always YES (empty subset).
    * ``target < 0`` is always NO.
    * An empty list is YES only when ``target == 0``.
    """
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for r in range(1, n + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == target:
                return True
    return False


def partition_bruteforce(numbers: List[int]) -> bool:
    """Return True iff *numbers* can be split into two groups of equal sum.

    Mirrors the semantics of the ``Partition`` problem:
    * Empty list → YES.
    * Odd total → NO.
    * Zeros are irrelevant – the brute‑force search naturally handles them.
    """
    total = sum(numbers)
    if total % 2:
        return False
    target = total // 2
    n = len(numbers)
    for r in range(n + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == target:
                return True
    return False


def run_tests(num_tests: int = 5000) -> Dict[str, Any]:
    """Generate random small instances, verify the reduction, and return stats.

    The function returns a dictionary compatible with the required ``verdict``
    JSON format.
    """
    passed = 0
    for i in range(num_tests):
        length = random.randint(0, 5)
        numbers = [random.randint(0, 5) for _ in range(length)]
        target = random.randint(-3, 10)
        source_instance: Dict[str, Any] = {"numbers": numbers, "target": target}
        try:
            SubsetSum.validate(source_instance)
        except Exception:
            continue
        src_ans = subset_sum_bruteforce(numbers, target)
        reduced = reduce_instance(source_instance)
        try:
            Partition.validate(reduced)
        except Exception:
            return {"verified": False, "tests_run": i + 1, "tests_passed": passed}
        tgt_ans = partition_bruteforce(reduced["numbers"])
        if src_ans == tgt_ans:
            passed += 1
        else:
            return {"verified": False, "tests_run": i + 1, "tests_passed": passed}
    return {"verified": True, "tests_run": num_tests, "tests_passed": passed}

if __name__ == "__main__":
    random.seed(0)
    verdict = run_tests()
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
