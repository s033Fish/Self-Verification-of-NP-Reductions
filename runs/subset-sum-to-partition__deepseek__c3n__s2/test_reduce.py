"""Tests for reduce.py: compare brute-force answers on many small instances."""

from __future__ import annotations

import itertools
import random

from problems import SubsetSum, Partition
from reduce import reduce


# ---------------------------------------------------------------- solvers
def subset_sum_solve(instance: dict) -> bool:
    """Brute force Subset Sum from the definition."""
    numbers = instance["numbers"]
    t = instance["target"]
    if t < 0:
        return False
    if t == 0:
        return True  # empty sub-list
    # enumerate all subsets (small instances only)
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == t:
                return True
    return False


def partition_solve(instance: dict) -> bool:
    """Brute force Partition from the definition."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    # find a subset summing to half (empty subset works when half == 0)
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == half:
                return True
    return False


# ---------------------------------------------------------------- tests
def check(instance: dict, results: list) -> None:
    SubsetSum.validate(instance)
    reduced = reduce(instance)
    Partition.validate(reduced)
    expected = subset_sum_solve(instance)
    got = partition_solve(reduced)
    assert expected == got, (
        f"MISMATCH source={instance} expected={expected} "
        f"reduced={reduced} got={got}"
    )
    results.append(1)


def main() -> None:
    results: list = []

    # 1. Edge cases explicitly from the docstrings.
    edge_cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 5},
        {"numbers": [], "target": -3},
        {"numbers": [0], "target": 0},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [5], "target": 0},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 3},
        {"numbers": [5], "target": -1},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [1, 2, 3], "target": 3},
        {"numbers": [2, 2], "target": 4},
        {"numbers": [2, 2], "target": 3},
        {"numbers": [1, 1, 1, 1], "target": 2},
        {"numbers": [0, 1, 2], "target": 3},
        {"numbers": [0, 1, 2], "target": 4},
    ]
    for inst in edge_cases:
        check(inst, results)

    # 2. Exhaustive small instances: all number-lists over small values,
    #    all targets in a range.
    for n in range(0, 6):
        for numbers in itertools.product(range(0, 4), repeat=n):
            for t in range(-2, sum(numbers) + 3):
                check({"numbers": list(numbers), "target": t}, results)

    # 3. Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        t = rng.randint(-3, sum(numbers) + 5)
        check({"numbers": numbers, "target": t}, results)

    # 4. Random instances biased toward exact-solvable targets.
    for _ in range(2000):
        n = rng.randint(1, 9)
        numbers = [rng.randint(0, 8) for _ in range(n)]
        if rng.random() < 0.7:
            subset = [x for x in numbers if rng.random() < 0.5]
            t = sum(subset)
        else:
            t = rng.randint(0, sum(numbers))
        check({"numbers": numbers, "target": t}, results)

    print(f"tests_run={len(results)} tests_passed={len(results)}")
    return len(results)


if __name__ == "__main__":
    main()
