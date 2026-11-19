"""Tests comparing brute-force answers on source instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import partition_solve, subset_sum_solve

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    expected = subset_sum_solve(instance)
    got = partition_solve(out)
    if expected != got:
        raise AssertionError(
            f"mismatch: source={instance} -> target={out}, "
            f"expected {expected}, got {got}"
        )
    tests_passed += 1


# ---- exhaustive small instances -------------------------------------------
for n in range(0, 6):
    for numbers in itertools.product(range(0, 5), repeat=n):
        total = sum(numbers)
        for target in range(-2, total + 3):
            check({"numbers": list(numbers), "target": target})

# ---- random instances with larger / repeated values ------------------------
rng = random.Random(12345)
for _ in range(3000):
    n = rng.randint(0, 10)
    numbers = [rng.choice([0, 1, 2, 3, 5, 8, 13, 100, 10**9]) for _ in range(n)]
    total = sum(numbers)
    target = rng.randint(-5, total + 5) if total > 0 else rng.randint(-5, 5)
    check({"numbers": numbers, "target": target})

# ---- explicit edge cases ---------------------------------------------------
edge_cases = [
    {"numbers": [], "target": 0},
    {"numbers": [], "target": 5},
    {"numbers": [], "target": -1},
    {"numbers": [0], "target": 0},
    {"numbers": [0, 0, 0], "target": 0},
    {"numbers": [5], "target": 5},
    {"numbers": [5], "target": 0},
    {"numbers": [5], "target": 3},
    {"numbers": [1, 1], "target": 1},
    {"numbers": [1, 1], "target": 2},
    {"numbers": [2, 2], "target": 2},
    {"numbers": [10**18, 10**18], "target": 10**18},
    {"numbers": [10**18, 1], "target": 1},
    {"numbers": [3, 3, 3], "target": 9},
    {"numbers": [3, 3, 3], "target": 6},
    {"numbers": [0, 7, 0], "target": 7},
]
for instance in edge_cases:
    check(instance)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
