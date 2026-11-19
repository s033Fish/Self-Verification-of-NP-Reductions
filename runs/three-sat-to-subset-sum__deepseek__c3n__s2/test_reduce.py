"""Tests for the 3-SAT -> Subset Sum reduction."""

import itertools
import random
import sys

from problems import ThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.


def solve_three_sat(instance: dict) -> bool:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        if all(
            any((lit > 0) == bits[abs(lit) - 1] for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def _subset_sums(values):
    sums = {0}
    for a in values:
        sums |= {s + a for s in sums}
    return sums


def solve_subset_sum(instance: dict) -> bool:
    """Exact subset sum via meet-in-the-middle (handles ~40 items)."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    half = len(numbers) // 2
    left = _subset_sums(numbers[:half])
    right = _subset_sums(numbers[half:])
    for s in left:
        if target - s in right:
            return True
    return False


# ----------------------------------------------------------------------
# Random small 3-SAT instance generator (valid per the docstring).


def random_three_sat(rng: random.Random, num_vars: int, num_clauses: int) -> dict:
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def run_tests() -> tuple[int, int]:
    tests_run = 0
    tests_passed = 0
    rng = random.Random(12345)

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(instance)
        reduced = reduce(instance)
        SubsetSum.validate(reduced)
        expected = solve_three_sat(instance)
        got = solve_subset_sum(reduced)
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", instance, "expected", expected, "got", got, "reduced", reduced)

    # Edge cases: no clauses, any m including 0.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 5, "clauses": []})

    # Random small formulas (kept small so brute force is fast).
    for _ in range(500):
        num_vars = rng.randint(3, 6)
        num_clauses = rng.randint(0, 6)
        check(random_three_sat(rng, num_vars, num_clauses))

    # A few larger ones (items <= 2*7 + 2*7 = 28 -> fine for MITM).
    for _ in range(60):
        num_vars = rng.randint(7, 8)
        num_clauses = rng.randint(1, 7)
        check(random_three_sat(rng, num_vars, num_clauses))

    # Hand-crafted cases.
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    # Unsatisfiable: all 8 clauses over 3 vars.
    all_clauses = [
        [signs[i] * (i + 1) for i in range(3)]
        for signs in itertools.product([1, -1], repeat=3)
    ]
    check({"num_vars": 3, "clauses": all_clauses})
    # Variables not appearing in any clause.
    check({"num_vars": 6, "clauses": [[1, 2, 3], [-1, -2, -3]]})

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    if run != passed:
        sys.exit(1)
