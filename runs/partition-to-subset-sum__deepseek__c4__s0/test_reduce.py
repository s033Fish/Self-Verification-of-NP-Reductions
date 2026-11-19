"""Test the Partition -> Subset Sum reduction against brute-force solvers."""

from __future__ import annotations

import itertools

from problems import Partition, SubsetSum
from reduce import reduce
from solvers import partition_solver, subset_sum_solver

tests_run = 0
tests_passed = 0


def check(numbers):
    global tests_run, tests_passed
    src = {"numbers": list(numbers)}
    Partition.validate(src)  # must be a valid source instance
    tgt = reduce(src)
    SubsetSum.validate(tgt)  # reduction must produce a valid target instance
    expected = partition_solver(src)
    got = subset_sum_solver(tgt)
    tests_run += 1
    if expected == got:
        tests_passed += 1
    else:
        print(f"FAIL: {src} -> {tgt}: expected {expected}, got {got}")


# Edge cases
check([])
check([0])
check([0, 0, 0])
check([1])
check([1, 1])
check([1, 2])
check([2, 2])
check([3, 1])
check([1000000000000000000, 1000000000000000000])

# Exhaustive over small multisets
for n in range(0, 8):
    for combo in itertools.combinations_with_replacement(range(0, 7), n):
        check(list(combo))

# Random-ish larger cases
import random

random.seed(12345)
for _ in range(3000):
    n = random.randint(0, 12)
    numbers = [random.randint(0, 30) for _ in range(n)]
    check(numbers)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"
