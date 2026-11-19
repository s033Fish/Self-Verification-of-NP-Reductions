"""Tests for reduce.py: compare Partition answer with reduced Subset Sum answer."""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from solvers import partition_yes, subset_sum_yes
from problems import Partition, SubsetSum

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    Partition.validate(instance)
    out = reduce(instance)
    SubsetSum.validate(out)
    expected = partition_yes(instance)
    got = subset_sum_yes(out)
    assert expected == got, (instance, out, expected, got)
    tests_passed += 1


def main() -> None:
    # Exhaustive over all small multisets with values 0..4, length 0..5.
    for n in range(0, 6):
        for combo in itertools.product(range(5), repeat=n):
            check({"numbers": list(combo)})

    # Exhaustive over values 0..2, length up to 7.
    for n in range(0, 8):
        for combo in itertools.product(range(3), repeat=n):
            check({"numbers": list(combo)})

    # Random larger instances with bigger values.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 20) for _ in range(n)]
        check({"numbers": numbers})

    # Instances with large values (arbitrary size ints).
    for _ in range(500):
        n = rng.randint(0, 8)
        numbers = [rng.randint(0, 10**18) for _ in range(n)]
        check({"numbers": numbers})

    # Specific edge cases.
    check({"numbers": []})
    check({"numbers": [0]})
    check({"numbers": [0, 0, 0]})
    check({"numbers": [1]})
    check({"numbers": [1, 1]})
    check({"numbers": [1, 2]})
    check({"numbers": [2, 2, 2]})
    check({"numbers": [10**30, 10**30]})
    check({"numbers": [10**30, 10**30 + 1]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
