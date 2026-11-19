"""Compare brute-force answers on source instances with answers on reductions."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import partition_yes, subset_sum_yes


def check(numbers, target):
    src = {"numbers": list(numbers), "target": target}
    SOURCE.validate(src)
    expected = subset_sum_yes(src["numbers"], target)

    tgt = reduce(src)
    TARGET.validate(tgt)
    got = partition_yes(tgt["numbers"])
    assert got == expected, (src, tgt, expected, got)
    return expected


def main():
    tests_run = 0

    # Exhaustive small cases: values 0..3, lists up to length 4, targets -2..8.
    for n in range(0, 5):
        for numbers in itertools.product(range(0, 4), repeat=n):
            for target in range(-2, 9):
                check(list(numbers), target)
                tests_run += 1

    # Random larger cases with bigger values.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 10)
        numbers = [rng.randint(0, 30) for _ in range(n)]
        target = rng.randint(-5, sum(numbers) + 5)
        check(numbers, target)
        tests_run += 1

    # Targeted edge cases.
    edges = [
        ([], 0),
        ([], 1),
        ([], -1),
        ([0], 0),
        ([0], 1),
        ([5], 5),
        ([5], 0),
        ([5], 3),
        ([1, 1], 2),
        ([1, 1], 1),
        ([2, 2, 2], 4),
        ([2, 2, 2], 6),
        ([1, 2, 3], 6),
        ([1, 2, 3], 3),
        ([1, 2, 3], 4),
        ([0, 0, 0], 0),
        ([7, 7, 7, 7], 14),
    ]
    for numbers, target in edges:
        check(numbers, target)
        tests_run += 1

    print(f"ALL PASSED: {tests_run} tests")
    return tests_run


if __name__ == "__main__":
    main()
