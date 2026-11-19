"""Independent verification of reduce.py (Subset Sum -> Partition).

We write our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare the source answer with the answer to
the reduced instance on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)
# ----------------------------------------------------------------------

def subset_sum_solver(instance: dict) -> bool:
    """True iff some sub-list of numbers sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def partition_solver(instance: dict) -> bool:
    """True iff positions can be split into two equal-sum groups."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == half:
            return True
    return False


SOLVERS = {SOURCE: subset_sum_solver, TARGET: partition_solver}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def check(instance: dict) -> tuple[bool, bool, dict]:
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    src_ans = subset_sum_solver(instance)
    tgt_ans = partition_solver(reduced)
    return src_ans, tgt_ans, reduced


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    # Exhaustive small instances.
    instances = []
    for n in range(0, 6):
        for numbers in itertools.product(range(0, 5), repeat=n):
            total = sum(numbers)
            for target in range(-2, total + 3):
                instances.append({"numbers": list(numbers), "target": target})

    # A few larger / random instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        total = sum(numbers)
        target = rng.randint(-3, total + 3)
        instances.append({"numbers": numbers, "target": target})

    for inst in instances:
        tests_run += 1
        try:
            src_ans, tgt_ans, reduced = check(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, "EXCEPTION", repr(exc)))
            continue
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append((inst, src_ans, tgt_ans, reduced))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print("  ", f)
    else:
        print("All reductions matched the brute-force answers.")

    # Sanity: solvers agree with documented edge cases.
    assert subset_sum_solver({"numbers": [], "target": 0}) is True
    assert subset_sum_solver({"numbers": [], "target": 1}) is False
    assert subset_sum_solver({"numbers": [1, 2], "target": -1}) is False
    assert partition_solver({"numbers": []}) is True
    assert partition_solver({"numbers": [1]}) is False
    assert partition_solver({"numbers": [1, 1]}) is True
    assert partition_solver({"numbers": [0, 0]}) is True
    print("Edge-case sanity checks passed.")


if __name__ == "__main__":
    main()
