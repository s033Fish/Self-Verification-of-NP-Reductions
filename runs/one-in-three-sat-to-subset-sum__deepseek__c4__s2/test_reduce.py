"""Tests for the 1-in-3-SAT -> Subset Sum reduction.

Contains independent brute-force solvers for both problems, written from the
problem definitions, and compares them on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of the reduction)

def solve_one_in_three_sat(instance: dict) -> bool:
    """True iff some assignment makes exactly one var true in every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            count = sum(1 for var in clause if bits[var - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """True iff some sub-list sums to the target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for value in numbers:
        reachable |= {s + value for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generators

def random_one_in_three_sat(rng: random.Random, max_vars: int = 7,
                            max_clauses: int = 6) -> dict:
    m = rng.randint(0, max_vars)
    if m < 3:
        clauses = []
    else:
        n = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(n):
            vars_ = rng.sample(range(1, m + 1), 3)
            rng.shuffle(vars_)
            clauses.append(vars_)
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests

def run_tests() -> tuple[int, int]:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        OneInThreeSat.validate(instance)
        reduced = reduce(instance)
        SubsetSum.validate(reduced)
        expected = solve_one_in_three_sat(instance)
        got = solve_subset_sum(reduced)
        if expected != got:
            raise AssertionError(
                f"mismatch on {instance}: source={expected}, target={got}, "
                f"reduced={reduced}"
            )
        tests_passed += 1

    # Hand-picked edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4]]},
        # No assignment makes exactly one true in both [1,2,3] and [1,2,4]
        # together with [3,4,?] style contradictions.
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [1, 2, 3], [4, 5, 6], [4, 5, 6]]},
        # Unused variable.
        {"num_vars": 4, "clauses": [[1, 2, 3]]},
    ]
    for inst in edge_cases:
        check(inst)

    # Exhaustive-ish random testing.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_one_in_three_sat(rng))

    # Exhaustive over all formulas with m = 3 and up to 3 clauses (sampled
    # clause multisets) to be thorough.
    all_clauses = list(itertools.combinations(range(1, 4), 3))
    for n in range(0, 4):
        for combo in itertools.combinations_with_replacement(all_clauses, n):
            check({"num_vars": 3, "clauses": [list(c) for c in combo]})

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed
    print("ALL TESTS PASSED")
