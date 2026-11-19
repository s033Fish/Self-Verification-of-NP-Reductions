"""Test the reduction from Partition to SubsetSum.

The script implements brute‑force solvers for both problems based on the
definitions in ``problems.py`` and then checks that for a large number of
small instances the answer of ``reduce.reduce`` matches the logical
equivalence required by the reduction.

The results are written to ``verdict.json`` in the repository root with the
following schema::

    {
        "verified": <bool>,
        "tests_run": <int>,
        "tests_passed": <int>
    }

The ``verified`` flag is true only when *all* generated test cases satisfy
the reduction property.
"""

from __future__ import annotations

import json
import itertools
import random
from typing import List, Dict

from problems import Partition, SubsetSum
from reduce import reduce as reduce_instance


def partition_bruteforce(numbers: List[int]) -> bool:
    """Return True iff the numbers can be split into two groups of equal sum.

    This follows the definition of the Partition problem.  An empty list is
    trivially YES.  Zeros do not affect the answer.
    """
    total = sum(numbers)
    if total % 2:
        return False
    target = total // 2
    # classic subset‑sum DP for non‑negative numbers
    reachable = {0}
    for x in numbers:
        new_reachable = set(reachable)
        for s in reachable:
            new_reachable.add(s + x)
        reachable = new_reachable
        if target in reachable:
            return True
    return target in reachable


def subset_sum_bruteforce(numbers: List[int], target: int) -> bool:
    """Return True iff a sub‑list of ``numbers`` sums to exactly ``target``.

    Handles the edge cases described in the problem statement.
    """
    if target < 0:
        return False
    if target == 0:
        return True
    # DP for non‑negative target
    reachable = {0}
    for x in numbers:
        new_reachable = set(reachable)
        for s in reachable:
            ns = s + x
            if ns == target:
                return True
            if ns < target:
                new_reachable.add(ns)
        reachable = new_reachable
    return target in reachable


def run_tests() -> Dict[str, int | bool]:
    tests_run = 0
    tests_passed = 0

    # Exhaustively test all small instances (length up to 5, values 0‑4).
    max_len = 5
    max_val = 4
    for length in range(max_len + 1):
        for numbers in itertools.product(range(max_val + 1), repeat=length):
            numbers = list(numbers)
            # Validate the source instance (should always succeed).
            Partition.validate({"numbers": numbers})
            # Compute expected answers.
            partition_answer = partition_bruteforce(numbers)
            # Reduce and solve using SubsetSum solver.
            reduced = reduce_instance({"numbers": numbers})
            # Ensure the reduction output validates.
            SubsetSum.validate(reduced)
            subset_answer = subset_sum_bruteforce(
                reduced["numbers"], reduced["target"]
            )
            tests_run += 1
            if partition_answer == subset_answer:
                tests_passed += 1
            else:
                # Print a diagnostic for debugging.
                print(
                    "Mismatch! numbers=",
                    numbers,
                    "partition=",
                    partition_answer,
                    "reduced=",
                    reduced,
                    "subset=",
                    subset_answer,
                )

    # Add a few random larger instances for extra confidence.
    random.seed(0)
    for _ in range(200):
        length = random.randint(0, 10)
        numbers = [random.randint(0, 20) for _ in range(length)]
        Partition.validate({"numbers": numbers})
        partition_answer = partition_bruteforce(numbers)
        reduced = reduce_instance({"numbers": numbers})
        SubsetSum.validate(reduced)
        subset_answer = subset_sum_bruteforce(
            reduced["numbers"], reduced["target"]
        )
        tests_run += 1
        if partition_answer == subset_answer:
            tests_passed += 1
        else:
            print(
                "Random mismatch! numbers=",
                numbers,
                "reduced=",
                reduced,
                "partition=",
                partition_answer,
                "subset=",
                subset_answer,
            )

    verified = tests_run == tests_passed
    return {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}


if __name__ == "__main__":
    result = run_tests()
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    # Also print the result for immediate visibility.
    print(json.dumps(result, indent=2))

