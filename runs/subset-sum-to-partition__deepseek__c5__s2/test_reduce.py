"""Independent checks of reduce.py: SubsetSum -> Partition.

We implement our own brute-force solvers from the problem definitions in
problems.py (which provides only validate), then compare the source answer
with the target answer on many small instances.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def subset_sum_solver(instance: dict) -> bool:
    """Yes iff some sub-list (each position at most once) sums to target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    # Enumerate all subsets of positions.
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == target:
                return True
    return False


def partition_solver(instance: dict) -> bool:
    """Yes iff positions split into two groups of equal sum."""
    numbers = instance["numbers"]
    total = sum(numbers)
    if total % 2 != 0:
        return False
    half = total // 2
    for r in range(len(numbers) + 1):
        for combo in itertools.combinations(numbers, r):
            if sum(combo) == half:
                return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    source_answer = subset_sum_solver(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)  # reduction must emit a valid target instance
    target_answer = partition_solver(reduced)
    if source_answer == target_answer:
        tests_passed += 1
    else:
        failures.append((instance, reduced, source_answer, target_answer))


def main() -> None:
    global tests_run, tests_passed
    rng = random.Random(12345)

    # 1. Exhaustive small instances: n = 0..4, values in 0..3,
    #    targets from -2 through sum+2.
    for n in range(0, 5):
        for values in itertools.product(range(0, 4), repeat=n):
            numbers = list(values)
            total = sum(numbers)
            for target in range(-2, total + 3):
                check({"numbers": list(numbers), "target": target})

    # 2. Exhaustive with zeros / repeats and larger targets.
    for n in range(0, 5):
        for values in itertools.product(range(0, 3), repeat=n):
            numbers = list(values)
            total = sum(numbers)
            for target in range(-3, total + 4):
                check({"numbers": list(numbers), "target": target})

    # 3. Random larger small instances (still brute-forceable).
    for _ in range(4000):
        n = rng.randint(0, 9)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        total = sum(numbers)
        target = rng.randint(-5, total + 5)
        check({"numbers": numbers, "target": target})

    # 4. Specific edge cases.
    edge = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -1},
        {"numbers": [0], "target": 0},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [5], "target": 0},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 3},
        {"numbers": [5], "target": -2},
        {"numbers": [1, 1, 1, 1], "target": 2},
        {"numbers": [1, 1, 1, 1], "target": 3},
        {"numbers": [2, 2, 2], "target": 3},
        {"numbers": [10**18, 10**18], "target": 10**18},
        {"numbers": [10**18, 10**18], "target": 1},
        {"numbers": [0, 10**18], "target": 10**18},
        {"numbers": [7, 7, 7], "target": 14},
        {"numbers": [7, 7, 7], "target": 21},
        {"numbers": [7, 7, 7], "target": 0},
    ]
    for inst in edge:
        check(inst)

    # 5. Polynomial-time sanity: a large instance should reduce quickly.
    import time
    big = {"numbers": [rng.randint(0, 10**9) for _ in range(200000)],
           "target": rng.randint(0, 10**9)}
    start = time.time()
    out = reduce(big)
    elapsed = time.time() - start
    tests_run += 1
    if len(out["numbers"]) == len(big["numbers"]) + 1 and elapsed < 5.0:
        tests_passed += 1
    else:
        failures.append(("large-instance", elapsed, None, None))

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)

    print("tests_run   =", tests_run)
    print("tests_passed=", tests_passed)
    print("failures    =", len(failures))
    for failure in failures[:10]:
        print("FAIL:", failure)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
