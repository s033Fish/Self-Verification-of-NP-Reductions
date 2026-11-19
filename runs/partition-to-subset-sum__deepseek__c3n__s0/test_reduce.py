"""Tests: brute-force solvers agree on source instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce
from solvers import partition_solver, subset_sum_solver

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    Partition.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = partition_solver(instance)
    got = subset_sum_solver(reduced)
    assert got == expected, (
        f"mismatch: {instance} -> {reduced}, "
        f"partition={expected}, subset_sum={got}"
    )
    tests_passed += 1


def main() -> None:
    # Hand-picked edge cases.
    edge_cases = [
        {"numbers": []},                 # empty -> yes
        {"numbers": [0]},                # yes
        {"numbers": [0, 0, 0]},          # yes
        {"numbers": [1]},                # odd total -> no
        {"numbers": [1, 2]},             # odd total -> no
        {"numbers": [1, 1]},             # yes
        {"numbers": [1, 2, 3]},          # yes (3 == 1+2)
        {"numbers": [1, 2, 4]},          # odd -> no
        {"numbers": [2, 2, 2]},          # odd total -> no
        {"numbers": [5, 5]},             # yes
        {"numbers": [3, 3, 3, 3]},       # yes
        {"numbers": [10**18, 10**18]},   # big numbers -> yes
        {"numbers": [10**18 + 1]},       # big odd -> no
        {"numbers": [7, 7, 7, 7, 7]},    # odd -> no
        {"numbers": [0, 5, 5]},          # yes
        {"numbers": [4, 4, 4, 4]},       # yes
        {"numbers": [1, 1, 1, 1, 1]},    # odd -> no
    ]
    for inst in edge_cases:
        check(inst)

    # Exhaustive over all small lists with values 0..4, lengths 0..6.
    for length in range(0, 7):
        for combo in itertools.product(range(0, 5), repeat=length):
            check({"numbers": list(combo)})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        length = rng.randint(0, 12)
        numbers = [rng.randint(0, 30) for _ in range(length)]
        check({"numbers": numbers})

    # Random instances with huge values (target arithmetic must stay exact).
    for _ in range(500):
        length = rng.randint(0, 8)
        numbers = [rng.randint(0, 10**15) for _ in range(length)]
        check({"numbers": numbers})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
