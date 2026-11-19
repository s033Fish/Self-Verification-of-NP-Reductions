"""Independent tests for reduce.py (Subset Sum -> Partition).

We implement our own brute-force solvers from the problem definitions and
compare their answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import SubsetSum, Partition
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the definitions, independent of reduce)
# ----------------------------------------------------------------------

def subset_sum_bruteforce(instance) -> bool:
    """Yes iff some sub-list of numbers sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def partition_bruteforce(instance) -> bool:
    """Yes iff positions split into two groups with equal sums."""
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


def solve_source(instance) -> bool:
    SubsetSum.validate(instance)
    return subset_sum_bruteforce(instance)


def solve_target(instance) -> bool:
    Partition.validate(instance)
    return partition_bruteforce(instance)


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    src_ans = solve_source(instance)
    reduced = reduce(instance)
    Partition.validate(reduced)  # must be a valid target instance
    tgt_ans = solve_target(reduced)
    if src_ans == tgt_ans:
        tests_passed += 1
    else:
        failures.append((instance, src_ans, reduced, tgt_ans))


def main():
    # 1. Exhaustive small instances.
    for n in range(0, 6):
        for numbers in itertools.product(range(0, 5), repeat=n):
            numbers = list(numbers)
            S = sum(numbers)
            # targets: negative, zero, in-range, above total
            targets = set(range(-3, S + 4))
            for t in sorted(targets):
                check({"numbers": list(numbers), "target": t})

    # 2. Random larger instances.
    rng = random.Random(12345)
    for _ in range(20000):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 30) for _ in range(n)]
        S = sum(numbers)
        t = rng.randint(-5, S + 5)
        check({"numbers": numbers, "target": t})

    # 3. Edge cases explicitly.
    edge = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -1},
        {"numbers": [0], "target": 0},
        {"numbers": [0], "target": 5},
        {"numbers": [1], "target": 1},
        {"numbers": [1], "target": 0},
        {"numbers": [5, 5], "target": 10},
        {"numbers": [5, 5], "target": 5},
        {"numbers": [3, 1, 1], "target": 2},
        {"numbers": [1000000000000, 1], "target": 1},
        {"numbers": [7], "target": 7},
        {"numbers": [7], "target": 14},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [2, 2], "target": 2},
    ]
    for inst in edge:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:20]:
            print("  ", f)
    return failures


if __name__ == "__main__":
    fails = main()
    raise SystemExit(1 if fails else 0)
