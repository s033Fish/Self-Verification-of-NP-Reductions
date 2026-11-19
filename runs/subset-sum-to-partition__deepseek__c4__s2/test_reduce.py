"""Tests for the Subset Sum -> Partition reduction.

We brute-force both problems on many small instances and check that
reduce() preserves the answer.  We also validate the produced instances
with problems.py's validators.
"""

from __future__ import annotations

import itertools

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import partition_bruteforce, subset_sum_bruteforce

tests_run = 0
tests_passed = 0


def check(source_instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1

    SOURCE.validate(source_instance)
    target_instance = reduce(source_instance)
    TARGET.validate(target_instance)

    expected = subset_sum_bruteforce(source_instance)
    got = partition_bruteforce(target_instance)

    assert got == expected, (
        f"mismatch on {source_instance}: "
        f"subset-sum={expected}, reduced partition={got}, "
        f"reduced instance={target_instance}"
    )
    tests_passed += 1


def main() -> None:
    # Exhaustive over small multisets and a range of targets, including
    # negative targets, t = 0, and targets beyond the total.
    values = [0, 1, 2, 3]
    for n in range(0, 5):
        for numbers in itertools.combinations_with_replacement(values, n):
            numbers = list(numbers)
            total = sum(numbers)
            targets = set(range(-3, total + 4))
            targets.update([0, total, total + 1, 2 * total + 5, -1, -100])
            for t in sorted(targets):
                check({"numbers": numbers, "target": t})

    # A few larger random-ish instances with bigger values.
    import random

    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        total = sum(numbers)
        t = rng.randint(-5, total + 5)
        check({"numbers": numbers, "target": t})

    # Big-value sanity checks (no brute force explosion: tiny n).
    for numbers, t in [
        ([10**18, 10**18], 10**18),
        ([10**18, 10**18], 1),
        ([5, 7, 11], 23),
        ([5, 7, 11], 0),
        ([], 0),
        ([], 1),
        ([], -1),
        ([0, 0, 0], 0),
        ([0, 0, 0], 1),
    ]:
        check({"numbers": numbers, "target": t})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
