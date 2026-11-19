"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce
from solvers import partition_brute, subset_sum_brute


def check(numbers):
    src = {"numbers": list(numbers)}
    Partition.validate(src)
    out = reduce(src)
    SubsetSum.validate(out)
    a = partition_brute(src)
    b = subset_sum_brute(out)
    assert a == b, f"mismatch for {numbers}: partition={a}, subset_sum={b}, out={out}"
    return a == b


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive small cases over a small value alphabet.
    for n in range(0, 7):
        for combo in itertools.product(range(4), repeat=n):
            tests_run += 1
            if check(list(combo)):
                tests_passed += 1

    # Random larger cases with bigger values and repeats.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 30) for _ in range(n)]
        tests_run += 1
        if check(numbers):
            tests_passed += 1

    # Hand-picked edge cases.
    edge_cases = [
        [],
        [0],
        [0, 0, 0],
        [1],
        [1, 1],
        [1, 2],
        [1, 2, 3],
        [2, 2, 2, 2],
        [3, 3, 3],
        [5, 5, 10],
        [0, 1, 2, 3],
        [10 ** 18, 10 ** 18],
        [10 ** 18, 10 ** 18 + 1],
        [7, 7, 7, 7, 7, 7],
    ]
    for numbers in edge_cases:
        tests_run += 1
        if check(numbers):
            tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
