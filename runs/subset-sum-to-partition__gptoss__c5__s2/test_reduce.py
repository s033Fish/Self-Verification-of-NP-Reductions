"""Test the reduction from Subset Sum to Partition.

The repository provides a ``reduce`` function that converts a Subset Sum
instance into a Partition instance.  Since the original problems do not have
solvers, we implement simple brute‑force solvers for both problems and verify
that for many small instances the answer of the reduced instance matches the
answer of the original instance.

The script counts how many test cases were generated and how many passed.  It
writes a ``verdict.json`` file with the required fields so that the evaluation
framework can read the result.
"""

from __future__ import annotations

import itertools
import json
import random
from pathlib import Path

from problems import SubsetSum, Partition
from reduce import reduce


def subset_sum_bruteforce(numbers: list[int], target: int) -> bool:
    """Return True iff a subset of ``numbers`` sums to ``target``.

    The definition follows the problem statement: each position may be used
    at most once.  ``numbers`` may contain zeros and duplicate values.
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


def partition_bruteforce(numbers: list[int]) -> bool:
    """Return True iff ``numbers`` can be split into two groups of equal sum.

    This is exactly the definition of the Partition problem.
    """
    total = sum(numbers)
    if total % 2:
        return False
    half = total // 2
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == half:
            return True
    return False


def generate_instances(max_len: int = 6, max_val: int = 5) -> list[dict]:
    """Generate a collection of Subset Sum instances for testing.

    ``max_len`` limits the number of numbers, ``max_val`` limits the value of
    each number.  For each list we also generate a range of target values that
    includes negative, zero, and values beyond the total sum to test edge
    cases.
    """
    instances = []
    for length in range(max_len + 1):
        for numbers in itertools.product(range(max_val + 1), repeat=length):
            numbers = list(numbers)
            total = sum(numbers)
            targets = set([-1, 0, 1, total - 1, total, total + 1, total + 2])
            for _ in range(3):
                targets.add(random.randint(-2, total + 2))
            for t in targets:
                instances.append({"numbers": numbers, "target": t})
    return instances


def main() -> None:
    instances = generate_instances()
    passed = 0
    for inst in instances:
        SubsetSum.validate(inst)
        ans_src = subset_sum_bruteforce(inst["numbers"], inst["target"])
        reduced = reduce(inst)
        Partition.validate(reduced)
        ans_tgt = partition_bruteforce(reduced["numbers"])
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", inst, "->", reduced, ans_src, ans_tgt)
            break
    total = len(instances)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

