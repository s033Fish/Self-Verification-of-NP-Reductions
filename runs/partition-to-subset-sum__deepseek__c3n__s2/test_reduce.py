"""Brute-force solvers and tests comparing Partition with its reduction."""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce


def solve_partition(instance):
    """Brute force: try every subset, check if it sums to half the total."""
    numbers = instance["numbers"]
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


def solve_subset_sum(instance):
    """Brute force: try every subset, check if any sums to the target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def check(instance):
    """Validate, reduce, validate the result, and compare answers."""
    Partition.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = solve_partition(instance)
    got = solve_subset_sum(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def main():
    tests_run = 0

    # Exhaustive small instances: all lists of length 0..6 over values 0..5.
    for n in range(0, 7):
        for combo in itertools.product(range(0, 6), repeat=n):
            check({"numbers": list(combo)})
            tests_run += 1

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 20) for _ in range(n)]
        check({"numbers": numbers})
        tests_run += 1

    # Explicit edge cases.
    for numbers in ([], [0], [0, 0], [1], [1, 1], [1, 2], [3, 1, 2],
                    [5, 5, 5, 5], [0, 0, 7], [2, 2, 2], [10 ** 30, 10 ** 30],
                    [10 ** 30 + 1]):
        check({"numbers": list(numbers)})
        tests_run += 1

    print(f"all {tests_run} tests passed")
    return tests_run


if __name__ == "__main__":
    main()
