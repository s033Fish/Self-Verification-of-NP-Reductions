"""Tests for the 3-SAT -> Subset Sum reduction in reduce.py.

Contains independent brute-force solvers for both problems (written from
the definitions in problems.py) and compares them on many small random
instances and edge cases.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)

def solve_three_sat(instance: dict) -> bool:
    """Try every assignment of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def _subset_sums(nums):
    sums = {0}
    for a in nums:
        sums |= {s + a for s in sums}
    return sums


def solve_subset_sum(instance: dict) -> bool:
    """Meet-in-the-middle exact subset-sum solver."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    half = len(numbers) // 2
    left = _subset_sums(numbers[:half])
    right = _subset_sums(numbers[half:])
    # Check whether any l + r == target.
    for l in left:
        if (target - l) in right:
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 8) -> dict:
    m = rng.randint(0, max_vars)
    if m < 3:
        # clauses require m >= 3, so only the empty formula is valid
        return {"num_vars": m, "clauses": []}
    k = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(k):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def check(instance: dict) -> bool:
    """Validate, reduce, validate target, compare solver answers."""
    ThreeSat.validate(instance)
    out = reduce(instance)
    SubsetSum.validate(out)
    return solve_three_sat(instance) == solve_subset_sum(out)


# ----------------------------------------------------------------------
# Tests

def main() -> int:
    tests_run = 0
    tests_passed = 0

    def run(name: str, condition: bool) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1
        else:
            print(f"FAIL: {name}")

    # Edge cases.
    run("empty formula m=0", check({"num_vars": 0, "clauses": []}))
    run("empty formula m=1", check({"num_vars": 1, "clauses": []}))
    run("empty formula m=5", check({"num_vars": 5, "clauses": []}))
    run("single clause", check({"num_vars": 3, "clauses": [[1, 2, 3]]}))
    run("single clause all neg", check({"num_vars": 3, "clauses": [[-1, -2, -3]]}))
    run("unsat small", check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3]]}))
    run("duplicate clause", check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}))
    run("unused vars", check({"num_vars": 6, "clauses": [[1, 2, 3]]}))
    run("mixed signs", check({"num_vars": 4, "clauses": [[1, -2, 3], [-1, 2, -4], [4, -3, 2]]}))

    # Random tests.
    rng = random.Random(12345)
    for _ in range(2000):
        inst = random_three_sat(rng)
        run(f"random {inst}", check(inst))

    # Slightly larger random tests (still brute-forceable).
    rng2 = random.Random(999)
    for _ in range(200):
        m = rng2.randint(3, 6)
        k = rng2.randint(0, 8)
        clauses = []
        for _ in range(k):
            vs = rng2.sample(range(1, m + 1), 3)
            clauses.append([v if rng2.random() < 0.5 else -v for v in vs])
        inst = {"num_vars": m, "clauses": clauses}
        run(f"random-large {inst}", check(inst))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_run == tests_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
