"""Test suite for the reduction from Partition to SubsetSum.

The repository provides only validation functions for the two problems.
This file implements straightforward brute‑force solvers for both
Partition and SubsetSum, enumerating all subsets of the given list of
non‑negative integers.  It then generates a variety of small instances,
applies the supplied ``reduce`` function and checks that the answer of the
generated SubsetSum instance matches the answer of the original Partition
instance.

If every generated test passes we consider the reduction verified.  The
script writes a ``verdict.json`` file with the required fields:

    {
        "verified": <bool>,
        "tests_run": <int>,
        "tests_passed": <int>
    }

The script is deliberately deterministic and runs quickly because the
search space is limited to small numbers (list length ≤ 6, each element ≤ 5).
"""

from __future__ import annotations

import json
import itertools
from pathlib import Path

from reduce import reduce as reduce_instance


def partition_bruteforce(numbers: list[int]) -> bool:
    """Return True iff the list can be partitioned into two equal‑sum groups.

    The definition from the problem statement is implemented directly:
    * An empty list is a yes‑instance.
    * If the total sum is odd the answer is False.
    * Otherwise we look for a subset whose sum is exactly total/2.
    """
    total = sum(numbers)
    if total % 2:
        return False
    target = total // 2
    # Enumerate all subsets using bit masks.
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def subsetsum_bruteforce(numbers: list[int], target: int) -> bool:
    """Return True iff some sub‑list sums exactly to *target*.

    Handles the edge cases from the specification:
    * target == 0 → always True (empty subset).
    * target < 0 → always False.
    """
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def generate_instances(max_len: int = 6, max_val: int = 5) -> list[dict]:
    """Generate a list of Partition instances.

    Each instance is a dict ``{"numbers": [...]}`` with length up to
    *max_len* and each entry between 0 and *max_val* inclusive.
    """
    instances = []
    for length in range(max_len + 1):
        for combo in itertools.product(range(max_val + 1), repeat=length):
            instances.append({"numbers": list(combo)})
    return instances


def main() -> None:
    instances = generate_instances()
    total = len(instances)
    passed = 0

    for inst in instances:
        numbers = inst["numbers"]
        # Compute the correct answers using the brute‑force solvers.
        partition_answer = partition_bruteforce(numbers)
        reduced = reduce_instance(inst)
        subset_answer = subsetsum_bruteforce(reduced["numbers"], reduced["target"])
        if partition_answer == subset_answer:
            passed += 1
        else:
            # For debugging, print the failing case.
            print("FAIL", inst, "reduced", reduced, partition_answer, subset_answer)

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
