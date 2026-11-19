"""Tests for the Partition -> Subset Sum reduction.

Contains brute-force solvers written from the problem definitions, and
compares their answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions)

def partition_solve(instance: dict) -> bool:
    """Yes iff positions can be split into two equal-sum groups."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(numbers)
    # Enumerate subsets via bitmask (fine for small n).
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == half:
            return True
    return False


def subset_sum_solve(instance: dict) -> bool:
    """Yes iff some sub-list sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


# ----------------------------------------------------------------------
# Tests

tests_run = 0
tests_passed = 0


def check(condition: bool, message: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        raise AssertionError(message)


def check_equivalence(instance: dict) -> None:
    Partition.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    src = partition_solve(instance)
    tgt = subset_sum_solve(reduced)
    check(
        src == tgt,
        f"mismatch: instance={instance!r} reduced={reduced!r} "
        f"partition={src} subset_sum={tgt}",
    )


def main() -> None:
    # Hand-picked edge cases.
    edge_cases = [
        {"numbers": []},                 # empty -> yes
        {"numbers": [0]},                # yes
        {"numbers": [1]},                # odd -> no
        {"numbers": [1, 1]},             # yes
        {"numbers": [1, 2]},             # odd -> no
        {"numbers": [1, 2, 3]},          # yes (1+2=3)
        {"numbers": [0, 0, 0]},          # yes
        {"numbers": [5]},                # no
        {"numbers": [2, 2, 2]},          # no (total 6, half 3 impossible)
        {"numbers": [3, 3]},             # yes
        {"numbers": [1, 1, 1, 1]},       # yes
        {"numbers": [4, 1, 1, 1, 1]},    # yes (4 = 1+1+1+1)
        {"numbers": [10, 1, 2, 3, 4]},   # yes (10 = 1+2+3+4)
        {"numbers": [1000000000000, 1000000000000]},  # big ints, yes
        {"numbers": [0, 5]},             # odd -> no
        {"numbers": [0, 4]},             # yes (0 vs 4? no) -> 4 even half=2 no
    ]
    for inst in edge_cases:
        check_equivalence(inst)

    # Exhaustive over all lists of length 0..7 with values 0..5.
    for n in range(0, 8):
        for combo in itertools.product(range(0, 6), repeat=n):
            check_equivalence({"numbers": list(combo)})

    # Random larger small instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 20) for _ in range(n)]
        check_equivalence({"numbers": numbers})

    # Random instances with larger values but small n.
    for _ in range(1000):
        n = rng.randint(0, 10)
        numbers = [rng.randint(0, 10**6) for _ in range(n)]
        check_equivalence({"numbers": numbers})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")


if __name__ == "__main__":
    main()
