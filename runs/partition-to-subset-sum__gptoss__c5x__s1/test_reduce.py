"""Independent tests for reduce.py (Partition -> Subset Sum).

We write our own brute-force solvers directly from the problem definitions
in problems.py (which provides only validate()), then compare the answers of
many small Partition instances with the answers of their reductions.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import Partition, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the definitions (NOT from reduce.py).

def partition_bruteforce(instance):
    """Yes iff positions can be split into two groups of equal sum.

    Enumerates every assignment of each position to group 0 or group 1.
    """
    numbers = instance["numbers"]
    n = len(numbers)
    for assignment in itertools.product((0, 1), repeat=n):
        s0 = sum(numbers[i] for i in range(n) if assignment[i] == 0)
        s1 = sum(numbers[i] for i in range(n) if assignment[i] == 1)
        if s0 == s1:
            return True
    return False


def subset_sum_bruteforce(instance):
    """Yes iff some sub-list (each position at most once) sums to target."""
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        total = 0
        for i in range(n):
            if mask & (1 << i):
                total += numbers[i]
        if total == target:
            return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(numbers):
    global tests_run, tests_passed
    src = {"numbers": list(numbers)}
    Partition.validate(src)
    expected = partition_bruteforce(src)
    reduced = reduce(src)
    SubsetSum.validate(reduced)
    got = subset_sum_bruteforce(reduced)
    tests_run += 1
    if expected == got:
        tests_passed += 1
    else:
        failures.append((list(numbers), expected, reduced, got))


def main():
    global tests_run, tests_passed
    # 1) Exhaustive small instances: all lists of length 0..6 with values 0..4.
    for n in range(0, 7):
        for combo in itertools.product(range(0, 5), repeat=n):
            check(combo)

    # 2) Exhaustive-ish instances with larger values and repeats.
    for n in range(0, 6):
        for combo in itertools.product(range(0, 8), repeat=n):
            check(combo)

    # 3) Random instances with bigger values (brute force still feasible).
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 30) for _ in range(n)]
        check(numbers)

    # 4) Explicit edge cases.
    edge_cases = [
        [],            # empty list -> yes
        [0],           # single zero -> yes
        [0, 0, 0],     # all zeros -> yes
        [1],           # odd total -> no
        [1, 2],        # odd total -> no
        [1, 1],        # yes
        [2, 2],        # yes
        [1, 1, 1],     # odd -> no
        [3, 1, 2],     # total 6, {3} vs {1,2} -> yes
        [3, 1, 3],     # total 7 odd -> no
        [5, 5, 5, 5],  # yes
        [7, 3, 2, 2],  # total 14, {7} vs {3,2,2} -> yes
        [7, 3, 2],     # total 12, {7} vs {3,2}? 7 vs 5 no; {7,?}... check
        [10, 0, 0],    # total 10, target 5 impossible -> no
        [100000000000000000000, 100000000000000000000],  # big ints -> yes
        [100000000000000000000, 1],  # odd -> no
    ]
    for numbers in edge_cases:
        check(numbers)

    # 5) Sanity: the reduction must not mutate its input.
    src = {"numbers": [1, 2, 3]}
    before = list(src["numbers"])
    reduce(src)
    tests_run += 1
    if src["numbers"] == before:
        tests_passed += 1
    else:
        failures.append(("input mutated", before, src["numbers"], None))

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    if failures:
        print("FAILURES (first 20):")
        for f in failures[:20]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")

    with open("test_output.json", "w") as fh:
        json.dump({"tests_run": tests_run, "tests_passed": tests_passed,
                   "failures": failures[:20]}, fh, indent=2)


if __name__ == "__main__":
    main()
