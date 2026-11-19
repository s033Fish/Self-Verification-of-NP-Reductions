"""Test suite for the reduction from Partition to SubsetSum.

The script defines brute‑force solvers for both problems based on the
definitions in ``problems.py`` and then checks that for a large collection of
small random instances the answer of the reduced SubsetSum instance matches
the answer of the original Partition instance.

It finally writes a ``verdict.json`` file containing the number of tests run,
how many passed and whether the reduction is verified.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict

# Import the problem definitions and the reduction implementation.
from problems import Partition, SubsetSum
from reduce import reduce as reduce_instance


def solve_partition(instance: Dict) -> bool:
    """Brute‑force solver for Partition.

    Returns ``True`` iff the numbers can be split into two groups with equal
    sum. Implements the definition directly: if the total sum is odd the
    answer is ``False``; otherwise we look for a subset that sums to half of
    the total.
    """
    numbers: List[int] = instance["numbers"]
    total = sum(numbers)
    if total % 2 == 1:
        return False
    target = total // 2
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def solve_subset_sum(instance: Dict) -> bool:
    """Brute‑force solver for SubsetSum.

    Returns ``True`` iff there exists a sub‑list of ``numbers`` that sums to
    ``target``. Handles the edge cases from the problem statement.
    """
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def generate_instances(max_len: int = 5, max_val: int = 5) -> List[Dict]:
    """Generate a list of Partition instances for testing.

    We enumerate all lists of length up to ``max_len`` whose elements are in
    ``0..max_val``. The total number of generated instances is modest (e.g.
    for the defaults it's ``(max_val+1)^{0+1+...+max_len}``).
    """
    instances: List[Dict] = []
    for length in range(max_len + 1):
        for combo in itertools.product(range(max_val + 1), repeat=length):
            instances.append({"numbers": list(combo)})
    return instances


def main() -> None:
    # Validate that the reduction function itself validates its input.
    Partition.validate({"numbers": []})

    instances = generate_instances()
    total = len(instances)
    passed = 0

    for inst in instances:
        expected = solve_partition(inst)
        reduced = reduce_instance(inst)
        SubsetSum.validate(reduced)
        actual = solve_subset_sum(reduced)
        if expected == actual:
            passed += 1
        else:
            print("Mismatch!", inst, "reduced to", reduced, file=sys.stderr)

    verified = passed == total
    verdict = {
        "verified": verified,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
