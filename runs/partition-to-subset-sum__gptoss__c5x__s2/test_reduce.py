"""Independent tests for reduce.py (Partition -> SubsetSum).

We implement brute-force solvers directly from the problem definitions in
problems.py (which provides no solvers), then compare the source answer with
the answer to the reduced instance on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.
# ----------------------------------------------------------------------

def partition_bruteforce(instance: dict) -> bool:
    """Yes iff positions can be split into two groups of equal sum."""
    Partition.validate(instance)
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    # Try every subset of positions (small n only).
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == half:
            return True
    return False


def subset_sum_bruteforce(instance: dict) -> bool:
    """Yes iff some sub-list sums to exactly the target."""
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
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


# ----------------------------------------------------------------------
# Test driver.
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    try:
        Partition.validate(instance)
    except Exception as exc:  # pragma: no cover
        failures.append((instance, f"source invalid: {exc}"))
        return
    reduced = reduce(instance)
    # The reduction must return a valid target instance.
    try:
        SubsetSum.validate(reduced)
    except Exception as exc:
        failures.append((instance, f"reduced instance invalid: {exc}"))
        return
    src = partition_bruteforce(instance)
    tgt = subset_sum_bruteforce(reduced)
    if src == tgt:
        tests_passed += 1
    else:
        failures.append((instance, f"source={src} target={tgt} reduced={reduced}"))


def main() -> None:
    # 1. Exhaustive over all lists of small length with small values.
    for n in range(0, 8):
        for combo in itertools.product(range(0, 5), repeat=n):
            check({"numbers": list(combo)})

    # 2. Exhaustive-ish with larger values / repeats.
    for n in range(0, 6):
        for combo in itertools.product(range(0, 9), repeat=n):
            check({"numbers": list(combo)})

    # 3. Random tests, including larger values and many zeros.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        check({"numbers": numbers})
    for _ in range(1000):
        n = rng.randint(0, 15)
        numbers = [rng.choice([0, 0, 0, 1, 2, 3, 100, 7]) for _ in range(n)]
        check({"numbers": numbers})

    # 4. Explicit edge cases.
    edge_cases = [
        {"numbers": []},
        {"numbers": [0]},
        {"numbers": [0, 0, 0]},
        {"numbers": [1]},
        {"numbers": [1, 1]},
        {"numbers": [1, 2]},
        {"numbers": [1, 2, 3]},
        {"numbers": [1, 1, 1, 1]},
        {"numbers": [5, 5]},
        {"numbers": [5, 5, 5]},
        {"numbers": [10**18, 10**18]},
        {"numbers": [10**18, 10**18 + 1]},
        {"numbers": [0, 0, 10**18, 10**18]},
    ]
    for inst in edge_cases:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for inst, msg in failures[:20]:
            print("  ", inst, "->", msg)
    else:
        print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
