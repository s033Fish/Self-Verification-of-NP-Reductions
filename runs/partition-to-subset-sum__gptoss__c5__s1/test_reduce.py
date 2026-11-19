"""Tests for the reduction from :class:`Partition` to :class:`SubsetSum`.

The repository provides a ``reduce`` function but no solvers.  This test
module implements straightforward brute‑force solvers for both problems
and checks that for a wide range of small instances the answer of the
reduced Subset‑Sum instance matches the answer of the original Partition
instance.

The test counts how many instances were examined and how many passed.
At the end it writes a ``verdict.json`` file with the required fields:

``{"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}``

The verification is considered successful only if **all** tested
instances satisfy the reduction property.
"""

from __future__ import annotations

import json
import itertools
import random
from pathlib import Path

from problems import Partition, SubsetSum
from reduce import reduce as reduce_instance


def partition_bruteforce(numbers: list[int]) -> bool:
    """Return True iff the list can be partitioned into two groups of equal sum.

    This follows the definition in the docstring of :class:`Partition`.
    """
    total = sum(numbers)
    if total % 2:
        return False
    target = total // 2
    # Re‑use subset‑sum brute‑force logic.
    return subset_sum_bruteforce(numbers, target)


def subset_sum_bruteforce(numbers: list[int], target: int) -> bool:
    """Return True iff some sub‑list of *numbers* sums to *target*.

    Implements the exact edge‑case handling described in the problem
    statement.
    """
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    # Simple exponential search – feasible for the tiny instances used in tests.
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def run_tests() -> tuple[int, int, bool]:
    """Execute a suite of random and exhaustive tests.

    Returns a tuple ``(tests_run, tests_passed, all_ok)``.
    """
    tests_run = 0
    tests_passed = 0
    all_ok = True

    # Exhaustive enumeration for small sizes.
    for length in range(0, 7):  # up to 6 elements
        # numbers are in 0..3 inclusive.
        for numbers in itertools.product(range(4), repeat=length):
            numbers = list(numbers)
            # Validate the source instance – should never raise.
            Partition.validate({"numbers": numbers})
            # Compute expected answers.
            expected_partition = partition_bruteforce(numbers)
            # Reduce and validate target instance.
            reduced = reduce_instance({"numbers": numbers})
            SubsetSum.validate(reduced)
            # Compute answer for reduced instance.
            got_subset = subset_sum_bruteforce(
                reduced["numbers"], reduced["target"]
            )
            ok = (expected_partition == got_subset)
            tests_run += 1
            if ok:
                tests_passed += 1
            else:
                all_ok = False
                # Print a diagnostic for the failing case.
                print(
                    "Mismatch! numbers=",
                    numbers,
                    "expected_partition=",
                    expected_partition,
                    "reduced=",
                    reduced,
                    "got_subset=",
                    got_subset,
                )

    # Additional random tests with larger values.
    random.seed(0)
    for _ in range(200):
        length = random.randint(0, 10)
        numbers = [random.randint(0, 20) for _ in range(length)]
        Partition.validate({"numbers": numbers})
        expected_partition = partition_bruteforce(numbers)
        reduced = reduce_instance({"numbers": numbers})
        SubsetSum.validate(reduced)
        got_subset = subset_sum_bruteforce(
            reduced["numbers"], reduced["target"]
        )
        ok = (expected_partition == got_subset)
        tests_run += 1
        if ok:
            tests_passed += 1
        else:
            all_ok = False
            print(
                "Random mismatch! numbers=",
                numbers,
                "expected=",
                expected_partition,
                "reduced=",
                reduced,
                "got=",
                got_subset,
            )

    return tests_run, tests_passed, all_ok


if __name__ == "__main__":
    run, passed, ok = run_tests()
    verdict = {
        "verified": ok,
        "tests_run": run,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
