"""Tests for the reduction from Partition to Subset Sum.

The test suite implements brute‑force solvers for both problems based on the
definitions in ``problems.py`` and checks that for a wide range of small
instances the answer to the original Partition instance matches the answer to
the reduced Subset Sum instance produced by ``reduce.py``.

The script records the number of tests executed and how many passed, then
writes a ``verdict.json`` file as required by the task description.
"""

from __future__ import annotations

import json
import random
from itertools import product

from problems import Partition, SubsetSum
from reduce import reduce as reduction


def solve_partition(instance: dict) -> bool:
    """Brute‑force solver for Partition.

    Returns True iff the numbers can be split into two groups of equal sum.
    """
    numbers = instance["numbers"]
    total = sum(numbers)
    # Edge cases handled by the definition
    if total % 2 != 0:
        return False
    target = total // 2
    # Subset‑sum DP for non‑negative numbers (small sizes only)
    reachable = {0}
    for x in numbers:
        reachable.update({s + x for s in list(reachable)})
    return target in reachable


def solve_subset_sum(instance: dict) -> bool:
    """Brute‑force solver for Subset Sum.

    Returns True iff some subset of ``numbers`` sums exactly to ``target``.
    """
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    # DP for non‑negative numbers; works because numbers are non‑negative.
    reachable = {0}
    for x in numbers:
        reachable.update({s + x for s in list(reachable) if s + x <= target})
    return target in reachable


def run_tests() -> tuple[int, int]:
    """Execute a battery of tests.

    Returns a tuple ``(tests_run, tests_passed)``.
    """
    tests_run = 0
    tests_passed = 0

    # Systematically enumerate small instances: length 0..5, values 0..4
    for length in range(0, 6):
        for numbers in product(range(0, 5), repeat=length):
            instance = {"numbers": list(numbers)}
            # Validate the source instance (should never raise)
            Partition.validate(instance)
            # Compute expected answers
            expected_partition = solve_partition(instance)
            # Apply reduction and validate target instance
            reduced = reduction(instance)
            SubsetSum.validate(reduced)
            # Compute answer on reduced instance
            answer_subset = solve_subset_sum(reduced)
            # The answers must match
            tests_run += 1
            if expected_partition == answer_subset:
                tests_passed += 1
            else:
                # For debugging, print the failing case
                print("FAIL", instance, "->", reduced,
                      expected_partition, answer_subset)

    # Add some random larger instances (still small enough for brute force)
    random.seed(0)
    for _ in range(200):
        length = random.randint(0, 8)
        numbers = [random.randint(0, 10) for _ in range(length)]
        instance = {"numbers": numbers}
        Partition.validate(instance)
        expected_partition = solve_partition(instance)
        reduced = reduction(instance)
        SubsetSum.validate(reduced)
        answer_subset = solve_subset_sum(reduced)
        tests_run += 1
        if expected_partition == answer_subset:
            tests_passed += 1
        else:
            print("FAIL RANDOM", instance, "->", reduced,
                  expected_partition, answer_subset)

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    verdict = {
        "verified": run == passed,
        "tests_run": run,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)
