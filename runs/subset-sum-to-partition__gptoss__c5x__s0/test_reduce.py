"""Independent tests for reduce.py (Subset Sum -> Partition).

We implement brute-force solvers directly from the problem definitions in
problems.py and compare them with the reduction on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import SubsetSum, Partition
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)

def subset_sum_solve(instance) -> bool:
    """True iff some sub-list of numbers sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    # enumerate all subsets (each position used at most once)
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == target:
                return True
    return False


def partition_solve(instance) -> bool:
    """True iff positions can be split into two equal-sum groups."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    # find a subset summing to half; the rest forms the other group
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == half:
                return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    src_ans = subset_sum_solve(instance)
    reduced = reduce(instance)
    # reduced must be a valid Partition instance
    try:
        Partition.validate(reduced)
    except Exception as exc:  # noqa: BLE001
        failures.append((instance, reduced, "invalid target instance", repr(exc)))
        return
    tgt_ans = partition_solve(reduced)
    if src_ans == tgt_ans:
        tests_passed += 1
    else:
        failures.append((instance, reduced, src_ans, tgt_ans))


# ----------------------------------------------------------------------
# 1. Exhaustive small instances

MAX_VAL = 4
MAX_LEN = 4
for length in range(MAX_LEN + 1):
    for numbers in itertools.product(range(MAX_VAL + 1), repeat=length):
        numbers = list(numbers)
        for target in range(-2, 11):
            check({"numbers": numbers, "target": target})

# ----------------------------------------------------------------------
# 2. Random larger instances

rng = random.Random(12345)
for _ in range(4000):
    length = rng.randint(0, 8)
    numbers = [rng.randint(0, 12) for _ in range(length)]
    target = rng.randint(-3, sum(numbers) + 5)
    check({"numbers": numbers, "target": target})

# ----------------------------------------------------------------------
# 3. Explicit edge cases

edge_cases = [
    {"numbers": [], "target": 0},
    {"numbers": [], "target": 1},
    {"numbers": [], "target": -1},
    {"numbers": [0], "target": 0},
    {"numbers": [0], "target": 1},
    {"numbers": [0, 0, 0], "target": 0},
    {"numbers": [0, 0, 0], "target": 5},
    {"numbers": [5], "target": 5},
    {"numbers": [5], "target": 2},
    {"numbers": [3, 3, 3], "target": 9},
    {"numbers": [3, 3, 3], "target": 1},
    {"numbers": [1, 1], "target": 2},
    {"numbers": [1, 1], "target": 1},
    {"numbers": [10**18, 10**18], "target": 10**18},
    {"numbers": [10**18, 1], "target": 10**18},
    {"numbers": [7, 7, 7, 7], "target": 14},
    {"numbers": [7, 7, 7, 7], "target": 15},
]
for inst in edge_cases:
    check(inst)

# ----------------------------------------------------------------------
# 4. Large-value random instances (values big, lengths small)

for _ in range(1000):
    length = rng.randint(0, 6)
    numbers = [rng.randint(0, 10**9) for _ in range(length)]
    target = rng.choice([rng.randint(-5, 5), rng.randint(0, sum(numbers) + 10)])
    check({"numbers": numbers, "target": target})

# ----------------------------------------------------------------------
# Report

print(f"tests_run = {tests_run}")
print(f"tests_passed = {tests_passed}")
print(f"failures = {len(failures)}")
for f in failures[:20]:
    print("FAIL:", f)

assert tests_passed == tests_run, "some reductions disagree with brute force"
print("ALL TESTS PASSED")
