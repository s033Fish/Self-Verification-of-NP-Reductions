"""Tests comparing brute-force answers on small Partition instances and their
reductions to Subset Sum."""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from solvers import partition_bruteforce, subset_sum_bruteforce

tests_run = 0
tests_passed = 0


def check(numbers):
    global tests_run, tests_passed
    tests_run += 1
    src = {"numbers": list(numbers)}
    tgt = reduce(src)
    expected = partition_bruteforce(src)
    got = subset_sum_bruteforce(tgt)
    assert got == expected, (src, tgt, expected, got)
    tests_passed += 1


# Exhaustive small instances with values 0..4 and lengths 0..6
for n in range(0, 7):
    for combo in itertools.product(range(0, 5), repeat=n):
        check(list(combo))

# Random larger instances
rng = random.Random(12345)
for _ in range(3000):
    n = rng.randint(0, 10)
    numbers = [rng.randint(0, 30) for _ in range(n)]
    check(numbers)

# Specific edge cases
check([])
check([0])
check([0, 0, 0])
check([1])
check([1, 2])
check([1, 1])
check([3, 3])
check([1, 2, 3])
check([1000000000000000000, 1000000000000000000])
check([1000000000000000000, 1000000000000000001])

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
