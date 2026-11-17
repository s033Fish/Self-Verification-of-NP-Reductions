"""Tests for the Subset Sum -> Partition reduction in reduce.py."""

import random

from problems import Partition, SubsetSum
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SubsetSum.validate(instance)
    reduced = reduce(instance)
    Partition.validate(reduced)
    expected = SubsetSum.is_yes(instance)
    got = Partition.is_yes(reduced)
    assert got == expected, (
        f"mismatch: source={instance} expected={expected} "
        f"reduced={reduced} got={got}"
    )
    tests_passed += 1


# 1. Exhaustive small instances (numbers 0..3, all targets).
for instance in SubsetSum.enumerate_instances(3):
    check(instance)

# 2. Explicit edge cases.
edge_cases = [
    {"numbers": [], "target": 0},          # empty list, t=0 -> yes
    {"numbers": [], "target": 1},          # empty list, t>0 -> no
    {"numbers": [], "target": -1},         # empty list, t<0 -> no
    {"numbers": [0], "target": 0},         # zeros
    {"numbers": [0, 0, 0], "target": 0},
    {"numbers": [0, 0, 0], "target": 1},
    {"numbers": [5], "target": 0},         # t=0 always yes
    {"numbers": [5], "target": 5},         # t=S
    {"numbers": [5], "target": 6},         # t>S
    {"numbers": [5], "target": -3},        # t<0
    {"numbers": [1, 2, 3], "target": 3},
    {"numbers": [1, 2, 3], "target": 4},
    {"numbers": [1, 2, 3], "target": 7},
    {"numbers": [4, 4, 4], "target": 8},
    {"numbers": [10, 20, 30], "target": 25},
    {"numbers": [10**18, 1], "target": 10**18},   # large values
    {"numbers": [10**18, 1], "target": 1},
    {"numbers": [10**18, 1], "target": 10**18 + 1},
]
for instance in edge_cases:
    check(instance)

# 3. Random instances at several scales.
rng = random.Random(12345)
for scale in range(0, 11):
    for _ in range(200):
        check(SubsetSum.random_instance(rng, scale))

# 4. Random instances with wider value ranges and targets.
for _ in range(2000):
    n = rng.randint(0, 8)
    numbers = [rng.randint(0, 12) for _ in range(n)]
    target = rng.randint(-3, sum(numbers) + 3)
    check({"numbers": numbers, "target": target})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
