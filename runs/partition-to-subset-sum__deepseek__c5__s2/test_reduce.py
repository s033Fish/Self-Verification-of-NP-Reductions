"""Independent verification of reduce.py: Partition -> Subset Sum.

We write our own brute-force solvers directly from the problem definitions
in problems.py (which provides no solvers), then compare the source answer
with the answer to the reduced target instance on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Partition, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions (no reuse of reduce.py)

def solve_partition(instance: dict) -> bool:
    """Yes iff positions split into two equal-sum groups."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    # brute force over all subsets (positions used at most once)
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == half:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Yes iff some sub-list sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True  # empty sub-list
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

tests_run = 0
tests_passed = 0
failures = []


def check(instance: dict, label: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    try:
        Partition.validate(instance)
    except Exception as exc:  # malformed source instance -> our bug
        failures.append(f"{label}: source instance invalid: {exc!r}")
        return
    src = solve_partition(instance)
    reduced = reduce(instance)
    # reduced must be a valid target instance
    try:
        SubsetSum.validate(reduced)
    except Exception as exc:
        failures.append(f"{label}: reduced instance invalid: {exc!r}")
        return
    tgt = solve_subset_sum(reduced)
    if src == tgt:
        tests_passed += 1
    else:
        failures.append(
            f"{label}: source={src} target={tgt} instance={instance} reduced={reduced}"
        )


def main() -> None:
    # --- explicit edge cases -------------------------------------------
    edge = [
        {"numbers": []},
        {"numbers": [0]},
        {"numbers": [0, 0, 0]},
        {"numbers": [1]},
        {"numbers": [1, 1]},
        {"numbers": [1, 2]},
        {"numbers": [1, 1, 1, 1]},
        {"numbers": [2, 2]},
        {"numbers": [3, 1]},
        {"numbers": [5, 5, 5, 5]},
        {"numbers": [0, 1, 1]},
        {"numbers": [0, 0, 2, 2]},
        {"numbers": [7]},
        {"numbers": [1000000000000000000000000000000, 1000000000000000000000000000000]},
        {"numbers": [10**30 + 1, 10**30 + 1]},
    ]
    for i, inst in enumerate(edge):
        check(inst, f"edge{i}")

    # --- exhaustive small instances ------------------------------------
    for n in range(0, 7):
        for combo in itertools.product(range(0, 5), repeat=n):
            check({"numbers": list(combo)}, f"exhaustive n={n} {combo}")

    # --- random instances ----------------------------------------------
    rng = random.Random(12345)
    for i in range(4000):
        n = rng.randint(0, 9)
        maxv = rng.choice([1, 2, 3, 5, 10, 50])
        nums = [rng.randint(0, maxv) for _ in range(n)]
        check({"numbers": nums}, f"random{i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print("  " + f)
    else:
        print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
