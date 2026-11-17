"""Tests comparing brute-force solvers on small Subset Sum instances and
their reductions to Partition."""

from __future__ import annotations

import itertools
import random

import problems
import reduce as reduce_module


def subset_sum_solver(instance: dict) -> bool:
    """Brute force: does any sub-list of numbers sum to target?"""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def partition_solver(instance: dict) -> bool:
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
            if mask >> i & 1:
                s += numbers[i]
        if s == half:
            return True
    return False


def check(instance: dict) -> bool:
    """Return True if the reduction preserves the answer."""
    problems.SubsetSum.validate(instance)
    expected = subset_sum_solver(instance)
    out = reduce_module.reduce(instance)
    problems.Partition.validate(out)
    got = partition_solver(out)
    assert expected == got, (instance, expected, out, got)
    return True


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if check(instance):
            tests_passed += 1

    # --- Hand-picked edge cases -------------------------------------
    hand = [
        {"numbers": [], "target": 0},          # empty list, t=0 -> yes
        {"numbers": [], "target": 1},          # empty list, t>0 -> no
        {"numbers": [], "target": -1},         # empty list, t<0 -> no
        {"numbers": [0], "target": 0},         # zeros
        {"numbers": [0, 0], "target": 0},
        {"numbers": [0], "target": 1},         # no
        {"numbers": [1], "target": 0},         # empty sub-list -> yes
        {"numbers": [1], "target": 1},         # yes
        {"numbers": [1], "target": 2},         # no (t > S)
        {"numbers": [1], "target": -5},        # no
        {"numbers": [5, 5], "target": 5},
        {"numbers": [5, 5], "target": 10},
        {"numbers": [5, 5], "target": 3},
        {"numbers": [2, 4, 6], "target": 6},
        {"numbers": [2, 4, 6], "target": 7},
        {"numbers": [3, 3, 3], "target": 9},
        {"numbers": [3, 3, 3], "target": 6},
        {"numbers": [3, 3, 3], "target": 1},
        {"numbers": [10**18, 10**18 + 1], "target": 10**18},
        {"numbers": [10**18, 10**18 + 1], "target": 1},
        {"numbers": [0, 0, 0, 5], "target": 5},
        {"numbers": [0, 0, 0, 5], "target": 0},
    ]
    for inst in hand:
        run(inst)

    # --- Exhaustive small instances ---------------------------------
    # All lists of length 0..4 with values in 0..3, all targets -2..14.
    values = range(4)
    for n in range(5):
        for combo in itertools.product(values, repeat=n):
            numbers = list(combo)
            for target in range(-2, 15):
                run({"numbers": numbers, "target": target})

    # --- Random larger instances ------------------------------------
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        total = sum(numbers)
        target = rng.randint(-3, total + 3)
        run({"numbers": numbers, "target": target})

    # --- Random instances with big values ---------------------------
    for _ in range(500):
        n = rng.randint(0, 6)
        numbers = [rng.randint(0, 10**15) for _ in range(n)]
        total = sum(numbers)
        target = rng.choice(
            [
                rng.randint(0, total) if total else 0,
                rng.randint(-2, total + 2) if total else 0,
                total,
                0,
            ]
        )
        run({"numbers": numbers, "target": target})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
