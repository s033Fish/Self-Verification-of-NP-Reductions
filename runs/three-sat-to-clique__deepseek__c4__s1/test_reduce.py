"""Brute-force solvers and tests for the 3-SAT -> Clique reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # bits[v-1] is the truth value of variable v
        if all(
            any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_clique(instance: dict) -> bool:
    """True iff the graph has a clique of size >= k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    for combo in itertools.combinations(range(n), k):
        if all(adj[a][b] for a, b in itertools.combinations(combo, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, valid instances).

def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 5):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        num_clauses = rng.randint(0, max_clauses)
        for _ in range(num_clauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustively enumerate tiny 3-SAT instances."""
    instances = []
    # no clauses, various m
    for m in range(0, 5):
        instances.append({"num_vars": m, "clauses": []})
    # m = 3, all possible clauses (order-insensitive, no repeated var)
    literals = [1, -1, 2, -2, 3, -3]
    clauses = []
    for combo in itertools.combinations(literals, 3):
        if len({abs(x) for x in combo}) == 3:
            clauses.append(list(combo))
    # every subset of clauses up to size 3
    for r in range(0, 4):
        for subset in itertools.combinations(clauses, r):
            instances.append({"num_vars": 3, "clauses": [list(c) for c in subset]})
    return instances


# ----------------------------------------------------------------------
# Tests

def run_tests() -> tuple[int, int]:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict, label: str):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(instance)
        reduced = reduce(instance)
        Clique.validate(reduced)
        expected = solve_three_sat(instance)
        got = solve_clique(reduced)
        if expected != got:
            raise AssertionError(
                f"FAIL {label}: source={instance} expected={expected} "
                f"reduced={reduced} got={got}"
            )
        tests_passed += 1

    # Exhaustive tiny cases
    for idx, inst in enumerate(all_small_three_sat()):
        check(inst, f"exhaustive-{idx}")

    # Random cases
    rng = random.Random(12345)
    for idx in range(2000):
        inst = random_three_sat(rng)
        check(inst, f"random-{idx}")

    # Larger random cases with more clauses
    for idx in range(200):
        m = rng.randint(3, 5)
        num_clauses = rng.randint(0, 5)
        clauses = []
        for _ in range(num_clauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
        check({"num_vars": m, "clauses": clauses}, f"larger-{idx}")

    # Explicit edge cases
    check({"num_vars": 0, "clauses": []}, "empty-m0")
    check({"num_vars": 7, "clauses": []}, "empty-m7")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single-sat")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two-clauses")
    # Unsatisfiable: all 8 clauses over 3 vars
    unsat = []
    for signs in itertools.product([1, -1], repeat=3):
        unsat.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    check({"num_vars": 3, "clauses": unsat}, "unsat-3vars")
    # Duplicate clauses
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate-clauses")

    return tests_run, tests_passed


if __name__ == "__main__":
    total, passed = run_tests()
    print(f"tests_run={total} tests_passed={passed}")
    assert total == passed
    print("ALL TESTS PASSED")
