"""Tests comparing brute-force answers on source instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, NaeThreeSat
from reduce import reduce
from solvers import solve_three_sat, solve_nae_three_sat

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    NaeThreeSat.validate(reduced)
    expected = solve_three_sat(instance)
    got = solve_nae_three_sat(reduced)
    assert got == expected, (
        f"mismatch: source={instance} expected={expected} "
        f"reduced={reduced} got={got}"
    )
    tests_passed += 1


def all_clauses(num_vars: int) -> list[list[int]]:
    """All valid 3-literal clauses over variables 1..num_vars."""
    clauses = []
    for combo in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, combo)])
    return clauses


def exhaustive_tests() -> None:
    # No-clause edge cases.
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []})

    # Exhaustively all formulas with up to 2 clauses over m = 3, 4 variables.
    for m in (3, 4):
        clauses = all_clauses(m)
        for c1 in clauses:
            check({"num_vars": m, "clauses": [c1]})
            for c2 in clauses:
                check({"num_vars": m, "clauses": [c1, c2]})

    # A few 3-clause formulas over m = 3.
    clauses = all_clauses(3)
    for c1 in clauses:
        for c2 in clauses:
            for c3 in clauses:
                check({"num_vars": 3, "clauses": [c1, c2, c3]})


def random_tests(n: int = 4000, seed: int = 12345) -> None:
    rng = random.Random(seed)
    for _ in range(n):
        m = rng.randint(0, 7)
        if m < 3:
            clauses = []
        else:
            k = rng.randint(0, 8)
            clauses = []
            for _ in range(k):
                vs = rng.sample(range(1, m + 1), 3)
                clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        check({"num_vars": m, "clauses": clauses})


def duplicate_clause_tests() -> None:
    # Repeated clauses must be handled.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, 3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3], [-1, -2, -4]]})


if __name__ == "__main__":
    exhaustive_tests()
    random_tests()
    duplicate_clause_tests()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
