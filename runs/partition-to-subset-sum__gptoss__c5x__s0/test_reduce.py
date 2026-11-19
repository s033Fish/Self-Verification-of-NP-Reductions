"""Independent tests for reduce.py (Partition -> Subset Sum).

We implement our own brute-force solvers straight from the problem
definitions in problems.py and compare:

    solve_partition(inst)  ==  solve_subset_sum(reduce(inst))

for many small source instances (exhaustive small cases + random cases).
"""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the docstrings.

def solve_partition(instance: dict) -> bool:
    """Partition: yes iff positions split into two equal-sum groups.

    Brute force over all 2^n assignments (position -> group 0/1).
    """
    Partition.validate(instance)
    numbers = instance["numbers"]
    n = len(numbers)
    for mask in range(1 << n):
        left = 0
        right = 0
        for i in range(n):
            if (mask >> i) & 1:
                left += numbers[i]
            else:
                right += numbers[i]
        if left == right:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Subset Sum: yes iff some sub-list sums to exactly target."""
    SubsetSum.validate(instance)
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
            if (mask >> i) & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


# ----------------------------------------------------------------------
# Test harness.

tests_run = 0
tests_passed = 0
failures = []


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    src = solve_partition(instance)
    reduced = reduce(instance)
    # The reduction must produce a valid target instance.
    SubsetSum.validate(reduced)
    tgt = solve_subset_sum(reduced)
    if src == tgt:
        tests_passed += 1
    else:
        failures.append((instance, reduced, src, tgt))


def main() -> None:
    # 1. Exhaustive: all lists of length 0..5 with values in 0..4.
    for n in range(0, 6):
        for combo in itertools.product(range(0, 5), repeat=n):
            check({"numbers": list(combo)})

    # 2. Exhaustive-ish: all lists of length 0..4 with values in 0..8.
    for n in range(0, 5):
        for combo in itertools.product(range(0, 9), repeat=n):
            check({"numbers": list(combo)})

    # 3. Random larger instances (still brute-forceable, n <= 14).
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 14)
        maxv = rng.choice([1, 2, 3, 5, 10, 100])
        nums = [rng.randint(0, maxv) for _ in range(n)]
        check({"numbers": nums})

    # 4. Hand-picked edge cases.
    edge_cases = [
        [],
        [0],
        [0, 0],
        [0, 0, 0],
        [1],
        [1, 1],
        [1, 2],
        [2, 2],
        [1, 1, 2],
        [3, 3, 3, 3],
        [10**18, 10**18],
        [10**18, 10**18, 1],
        [0, 10**30, 10**30],
        [7, 7, 7],
        [5, 5, 5, 5, 5],
    ]
    for nums in edge_cases:
        check({"numbers": nums})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for inst, red, s, t in failures[:10]:
            print("  src:", inst, "->", red, "partition:", s, "subset:", t)
    else:
        print("ALL PASSED")


if __name__ == "__main__":
    main()
