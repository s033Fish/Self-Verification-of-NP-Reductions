"""Independent brute-force check of reduce.py (Subset Sum -> Partition).

We implement our own solvers directly from the problem definitions in
problems.py (which provides only validate()), then compare the answer of every
small source instance with the answer of its reduction.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import SubsetSum, Partition
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_subset_sum(instance):
    """Yes iff some sub-list of numbers sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


def solve_partition(instance):
    """Yes iff positions split into two groups of equal sum."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return half in reachable


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(source_instance):
    global tests_run, tests_passed
    tests_run += 1
    try:
        SubsetSum.validate(source_instance)
        before = repr(source_instance)
        target_instance = reduce(source_instance)
        assert repr(source_instance) == before, "reduce mutated its input"
        Partition.validate(target_instance)
        expected = solve_subset_sum(source_instance)
        got = solve_partition(target_instance)
        if expected != got:
            failures.append((source_instance, target_instance, expected, got))
            return
        tests_passed += 1
    except Exception as exc:  # noqa: BLE001
        failures.append((source_instance, "EXC", repr(exc), None))


def exhaustive():
    values = [0, 1, 2, 3, 4]
    for n in range(0, 5):
        for nums in itertools.product(values, repeat=n):
            nums = list(nums)
            S = sum(nums)
            for t in range(-2, S + 3):
                check({"numbers": nums, "target": t})


def randomized():
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 8)
        nums = [rng.randint(0, 12) for _ in range(n)]
        S = sum(nums)
        check({"numbers": nums, "target": rng.randint(-3, S + 3)})
    for _ in range(1500):
        n = rng.randint(0, 6)
        nums = [rng.choice([0, 1, 5, 10, 25, 100]) for _ in range(n)]
        S = sum(nums)
        check({"numbers": nums, "target": rng.randint(-1, S + 1)})
    # larger instances, sparse values
    for _ in range(3000):
        n = rng.randint(0, 14)
        nums = [rng.choice([0, 1, 2, 3, 7, 13, 50, 200]) for _ in range(n)]
        S = sum(nums)
        check({"numbers": nums, "target": rng.randint(-2, S + 2)})


def edge_cases():
    cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -1},
        {"numbers": [0], "target": 0},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 0},
        {"numbers": [5], "target": 3},
        {"numbers": [10**30, 10**30], "target": 10**30},
        {"numbers": [10**30, 10**30], "target": 1},
        {"numbers": [10**30, 10**30], "target": 2 * 10**30},
        {"numbers": [10**30, 10**30], "target": 2 * 10**30 + 1},
        {"numbers": [1, 2, 3], "target": 3},
        {"numbers": [1, 2, 3], "target": 4},
    ]
    for c in cases:
        check(c)


if __name__ == "__main__":
    exhaustive()
    randomized()
    edge_cases()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:20]:
            print("  ", f)
    else:
        print("ALL PASSED")
    verdict = {
        "verified": len(failures) == 0 and tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
