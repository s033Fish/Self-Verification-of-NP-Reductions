"""Brute-force solvers and tests for the Partition -> Subset Sum reduction."""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_partition(instance) -> bool:
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    target = total // 2
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def solve_subset_sum(instance) -> bool:
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

def test_exhaustive_small():
    tests_run = 0
    tests_passed = 0
    # Exhaustive over all multisets of small values with length <= 5.
    values = [0, 1, 2, 3, 4]
    for n in range(0, 6):
        for combo in itertools.combinations_with_replacement(values, n):
            src = {"numbers": list(combo)}
            Partition.validate(src)
            tgt = reduce(src)
            SubsetSum.validate(tgt)
            expected = solve_partition(src)
            got = solve_subset_sum(tgt)
            tests_run += 1
            if expected == got:
                tests_passed += 1
            else:
                raise AssertionError(f"MISMATCH src={src} tgt={tgt} expected={expected} got={got}")
    return tests_run, tests_passed


def test_random():
    tests_run = 0
    tests_passed = 0
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 10)
        src = {"numbers": [rng.randint(0, 12) for _ in range(n)]}
        Partition.validate(src)
        tgt = reduce(src)
        SubsetSum.validate(tgt)
        expected = solve_partition(src)
        got = solve_subset_sum(tgt)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            raise AssertionError(f"MISMATCH src={src} tgt={tgt} expected={expected} got={got}")
    return tests_run, tests_passed


def test_edge_cases():
    tests_run = 0
    tests_passed = 0
    cases = [
        [],
        [0],
        [0, 0, 0],
        [1],
        [1, 1],
        [1, 2],
        [2, 2],
        [3, 3, 3],
        [1000000000000000000, 1000000000000000000],
        [5, 5, 5, 5],
    ]
    for numbers in cases:
        src = {"numbers": list(numbers)}
        Partition.validate(src)
        tgt = reduce(src)
        SubsetSum.validate(tgt)
        expected = solve_partition(src)
        got = solve_subset_sum(tgt)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            raise AssertionError(f"MISMATCH src={src} tgt={tgt} expected={expected} got={got}")
    return tests_run, tests_passed


if __name__ == "__main__":
    total_run = 0
    total_passed = 0
    for fn in (test_exhaustive_small, test_random, test_edge_cases):
        r, p = fn()
        total_run += r
        total_passed += p
        print(f"{fn.__name__}: {p}/{r} passed")
    print(f"TOTAL: {total_passed}/{total_run} passed")

    import json
    verified = total_passed == total_run
    with open("verdict.json", "w") as f:
        json.dump({"verified": verified, "tests_run": total_run, "tests_passed": total_passed}, f)
    print("verdict.json written:", verified)
