"""Tests: brute-force source/target solvers vs. the reduction."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import partition_solver, subset_sum_solver

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
    assert got == expected, (
        f"mismatch on {instance!r}: source={expected}, "
        f"reduced={reduced!r} target={got}"
    )
    tests_passed += 1


def main():
    # Exhaustive: all multisets of length 0..4 with values 0..4, all targets
    # in a range covering negatives, zero, exact sums and overshoots.
    values = [0, 1, 2, 3, 4]
    for n in range(0, 5):
        for combo in itertools.combinations_with_replacement(values, n):
            for target in range(-3, sum(combo) + 4):
                check({"numbers": list(combo), "target": target})

    # Exhaustive: length 5 with values 0..3.
    for combo in itertools.combinations_with_replacement([0, 1, 2, 3], 5):
        for target in range(-2, sum(combo) + 3):
            check({"numbers": list(combo), "target": target})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 20) for _ in range(n)]
        target = rng.randint(-5, sum(numbers) + 5)
        check({"numbers": numbers, "target": target})

    # Random instances with large values (reduction must not depend on size).
    for _ in range(1000):
        n = rng.randint(0, 8)
        numbers = [rng.randint(0, 10**12) for _ in range(n)]
        target = rng.randint(-2, sum(numbers) + 2)
        check({"numbers": numbers, "target": target})

    # Specific edge cases.
    for instance in [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -1},
        {"numbers": [0], "target": 0},
        {"numbers": [0, 0], "target": 0},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 0},
        {"numbers": [5], "target": 3},
        {"numbers": [1, 1], "target": 2},
        {"numbers": [1, 1], "target": 1},
        {"numbers": [1, 2, 3], "target": 3},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [0, 0, 0], "target": 0},
    ]:
        check(instance)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")


if __name__ == "__main__":
    main()
