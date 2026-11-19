"""Tests for the Partition -> Subset Sum reduction.

problems.py has no solvers, so we implement brute-force solvers from the
definitions, then compare answers on many small source instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def partition_solver(instance: dict) -> bool:
    """Yes iff positions can be split into two equal-sum groups."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(numbers)
    # Try every subset as one group; the rest is the other group.
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == half:
            return True
    return False


def subset_sum_solver(instance: dict) -> bool:
    """Yes iff some sub-list sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
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
# Test harness

tests_run = 0
tests_passed = 0


def check(condition: bool, message: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        print(f"FAIL: {message}")


def check_reduction(numbers: list[int]) -> None:
    src = {"numbers": list(numbers)}
    Partition.validate(src)
    tgt = reduce(src)
    SubsetSum.validate(tgt)

    src_answer = partition_solver(src)
    tgt_answer = subset_sum_solver(tgt)

    check(
        src_answer == tgt_answer,
        f"mismatch for {numbers}: partition={src_answer}, "
        f"reduced={tgt} subset_sum={tgt_answer}",
    )


# ----------------------------------------------------------------------
# 1. Edge cases from the docstrings.

check_reduction([])                 # empty list -> yes
check_reduction([0])                # zeros -> yes
check_reduction([0, 0, 0])          # zeros -> yes
check_reduction([1])                # odd total -> no
check_reduction([1, 2])             # odd total -> no
check_reduction([5, 5])             # yes
check_reduction([1, 1, 1, 1])       # yes
check_reduction([1, 1, 1])          # odd total -> no
check_reduction([10])               # even total but 10 != 0 -> no
check_reduction([2, 2])             # yes
check_reduction([1, 3])             # yes
check_reduction([1, 2, 3])          # yes (1+2 = 3)
check_reduction([1, 2, 4])          # no (7 odd)
check_reduction([2, 4, 6])          # yes (2+4=6)
check_reduction([3, 3, 3, 3])       # yes
check_reduction([1000000000000, 1000000000000])  # big ints -> yes
check_reduction([1000000000001, 1000000000000])  # big ints odd -> no

# 2. Exhaustive small instances over small values.

for n in range(0, 8):
    for values in itertools.product(range(4), repeat=n):
        check_reduction(list(values))

# 3. Exhaustive with a couple of larger values mixed in.

for n in range(0, 6):
    for values in itertools.product(range(6), repeat=n):
        check_reduction(list(values))

# 4. Random instances with larger values.

rng = random.Random(12345)
for _ in range(3000):
    n = rng.randint(0, 10)
    numbers = [rng.randint(0, 30) for _ in range(n)]
    check_reduction(numbers)

# 5. Random instances with huge integers (polynomial-time reduction must
#    handle arbitrary-size values without enumerating them).

for _ in range(500):
    n = rng.randint(0, 8)
    numbers = [rng.randint(0, 10**18) for _ in range(n)]
    check_reduction(numbers)

# 6. Verify the reduction output format explicitly on a few cases.

tgt = reduce({"numbers": [1, 2, 3]})
check(tgt == {"numbers": [1, 2, 3], "target": 3}, f"unexpected output {tgt}")

tgt = reduce({"numbers": [1, 2]})
check(tgt == {"numbers": [1, 2], "target": 4}, f"unexpected output {tgt}")

tgt = reduce({"numbers": []})
check(tgt == {"numbers": [], "target": 0}, f"unexpected output {tgt}")

# 7. Reduction must not mutate its input.

src = {"numbers": [1, 2, 3]}
before = list(src["numbers"])
reduce(src)
check(src == {"numbers": before}, "reduce mutated its input")

print(f"tests_run={tests_run}, tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"
