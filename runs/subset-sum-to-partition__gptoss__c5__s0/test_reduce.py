"""Test suite for the reduction from SubsetSum to Partition.

This file defines a brute‑force solver for both problems and then checks that
the ``reduce`` function from ``reduce.py`` preserves the answer on a large set
of small randomly generated instances.  The module provides a ``run_checks``
function that returns a tuple ``(tests_run, tests_passed)`` which is used by
the verification script to produce ``verdict.json``.
"""

from __future__ import annotations

from itertools import product
from typing import List, Tuple, Dict

from reduce import reduce  # The reduction under test
from problems import SubsetSum, Partition


def brute_force_subset_sum(numbers: List[int], target: int) -> bool:
    """Return True iff some sub‑list of *numbers* sums to *target*.

    The implementation enumerates all subsets via bit masks – sufficient for
    the tiny instances used in the test suite.
    """
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def brute_force_partition(numbers: List[int]) -> bool:
    """Return True iff the multiset *numbers* can be split into two equal‑sum groups.
    """
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == half:
            return True
    return False


def generate_instances() -> List[Dict]:
    """Generate a collection of small SubsetSum instances.

    Numbers are taken from 0..3, list length up to 5, and target from -2..6.
    This yields a modest number of instances that still cover edge cases.
    """
    instances: List[Dict] = []
    max_len = 5
    for length in range(max_len + 1):
        for numbers in product(range(4), repeat=length):
            nums = list(numbers)
            for target in range(-2, 7):
                instances.append({"numbers": nums, "target": target})
    return instances


def run_checks() -> Tuple[int, int]:
    """Run the reduction verification on all generated instances.

    Returns a tuple ``(tests_run, tests_passed)``.
    """
    instances = generate_instances()
    tests_run = 0
    tests_passed = 0
    for inst in instances:
        SubsetSum.validate(inst)
        ss_answer = brute_force_subset_sum(inst["numbers"], inst["target"])
        part_inst = reduce(inst)
        Partition.validate(part_inst)
        part_answer = brute_force_partition(part_inst["numbers"])
        tests_run += 1
        if ss_answer == part_answer:
            tests_passed += 1
    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_checks()
    print(f"Ran {run} tests, {passed} passed.")
