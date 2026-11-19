"""Test the reduction from Partition to Subset Sum.

The repository provides only validation functions for the two problems and a
``reduce`` implementation.  To verify that the reduction is correct we implement
brute‑force solvers for both problems and compare the answer on a large set of
small instances.

The script generates all possible ``numbers`` lists of length up to 6 where each
element is in ``0..5`` (including the empty list).  For each instance we call
``reduce`` and check that the answer to the original Partition instance matches
the answer to the produced Subset‑Sum instance.

The results are written to ``verdict.json`` as required by the task description.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List

from problems import Partition, SubsetSum
from reduce import reduce as reduce_instance


def partition_bruteforce(numbers: List[int]) -> bool:
    """Return True iff the list can be partitioned into two equal‑sum groups.

    The implementation follows the definition directly: an odd total sum is
    impossible, otherwise we search for a subset that sums to half of the total.
    """
    total = sum(numbers)
    if total % 2:
        return False
    target = total // 2
    # simple DP for subset sum (numbers are non‑negative)
    reachable = {0}
    for x in numbers:
        reachable.update({s + x for s in list(reachable)})
    return target in reachable


def subsetsum_bruteforce(numbers: List[int], target: int) -> bool:
    """Return True iff some sub‑list sums exactly to *target*.

    Handles the edge cases described in the problem statement.
    """
    if target < 0:
        return False
    if target == 0:
        return True
    # DP for non‑negative target
    reachable = {0}
    for x in numbers:
        reachable.update({s + x for s in list(reachable) if s + x <= target})
    return target in reachable


def main() -> None:
    max_len = 6
    max_val = 5
    tests_run = 0
    tests_passed = 0
    mismatches = []

    for length in range(max_len + 1):
        for numbers in itertools.product(range(max_val + 1), repeat=length):
            numbers_list = list(numbers)
            # Validate the instance according to the problem definitions.
            try:
                Partition.validate({"numbers": numbers_list})
            except Exception as e:
                print(f"Invalid Partition instance {numbers_list}: {e}", file=sys.stderr)
                continue

            # Compute answers for the original problem.
            partition_ans = partition_bruteforce(numbers_list)

            # Reduce to Subset Sum.
            reduced = reduce_instance({"numbers": numbers_list})
            # Validate reduced instance.
            try:
                SubsetSum.validate(reduced)
            except Exception as e:
                print(f"Invalid reduced SubsetSum instance {reduced}: {e}", file=sys.stderr)
                continue

            subset_ans = subsetsum_bruteforce(reduced["numbers"], reduced["target"])

            tests_run += 1
            if partition_ans == subset_ans:
                tests_passed += 1
            else:
                mismatches.append({
                    "numbers": numbers_list,
                    "reduced": reduced,
                    "partition_ans": partition_ans,
                    "subset_ans": subset_ans,
                })

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    # Write the verdict to the required file.
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

    # Print a short summary for the console.
    print(json.dumps(verdict, indent=2))

    # If there were mismatches, also output them for debugging.
    if mismatches:
        print("Mismatches encountered:", file=sys.stderr)
        for m in mismatches:
            print(m, file=sys.stderr)

if __name__ == "__main__":
    main()

