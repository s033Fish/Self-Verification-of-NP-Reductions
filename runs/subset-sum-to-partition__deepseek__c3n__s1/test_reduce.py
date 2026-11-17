"""Brute-force solvers plus randomized/exhaustive tests for reduce()."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


def subset_sum_solver(instance) -> bool:
    """Brute force: is there a sub-list summing exactly to target?"""
    numbers = instance["numbers"]
    target = instance["target"]
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == target:
                return True
    return False


def partition_solver(instance) -> bool:
    """Brute force: can positions be split into two equal-sum groups?"""
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


tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = subset_sum_solver(instance)
    got = partition_solver(reduced)
    assert expected == got, (
        f"mismatch: source={instance} expected={expected} "
        f"reduced={reduced} got={got}"
    )
    tests_passed += 1


def main():
    # Edge cases from the docstrings.
    edge_cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 5},
        {"numbers": [], "target": -3},
        {"numbers": [0], "target": 0},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [5], "target": 0},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 3},
        {"numbers": [5], "target": -1},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [1, 2, 3], "target": 100},
        {"numbers": [1, 1, 1, 1], "target": 2},
        {"numbers": [2, 2, 2], "target": 4},
        {"numbers": [10, 0, 0], "target": 10},
        {"numbers": [3, 3, 3, 3], "target": 6},
    ]
    for inst in edge_cases:
        check(inst)

    # Exhaustive small instances.
    for n in range(0, 6):
        for numbers in itertools.product(range(0, 5), repeat=n):
            numbers = list(numbers)
            for target in range(-2, sum(numbers) + 3):
                check({"numbers": numbers, "target": target})

    # Random larger instances (still brute-forceable).
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 20) for _ in range(n)]
        target = rng.randint(-5, sum(numbers) + 5)
        check({"numbers": numbers, "target": target})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
