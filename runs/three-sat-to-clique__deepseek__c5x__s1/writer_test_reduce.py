"""Brute-force solvers and randomized/exhaustive tests for the 3-SAT -> Clique reduction."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_three_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause. No clauses -> yes."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # variable v (1..m) is bits[v-1]
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance: dict) -> bool:
    """Yes iff graph has a clique of at least k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for subset in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, valid instances).

def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 4) -> dict:
    m = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustively enumerate small 3-SAT instances."""
    instances = []
    # no clauses, various m
    for m in range(0, 5):
        instances.append({"num_vars": m, "clauses": []})
    # m = 3, all possible single clauses (ordered literals over 3 vars)
    for signs in itertools.product([1, -1], repeat=3):
        clause = [signs[0] * 1, signs[1] * 2, signs[2] * 3]
        instances.append({"num_vars": 3, "clauses": [clause]})
    # m = 3, all pairs of clauses (with repetition allowed)
    base = []
    for signs in itertools.product([1, -1], repeat=3):
        base.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    for c1 in base:
        for c2 in base:
            instances.append({"num_vars": 3, "clauses": [list(c1), list(c2)]})
    return instances


def main():
    tests_run = 0
    tests_passed = 0

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = solve_three_sat(inst)
        reduced = reduce(inst)
        # validate target format using problems.py
        from problems import Clique, ThreeSat
        ThreeSat.validate(inst)
        Clique.validate(reduced)
        got = solve_clique(reduced)
        assert got == expected, (
            f"MISMATCH for {inst}: 3-SAT={expected}, Clique={got}, reduced={reduced}"
        )
        tests_passed += 1

    # exhaustive small instances
    for inst in all_small_three_sat():
        check(inst)

    # randomized instances
    rng = random.Random(12345)
    for _ in range(400):
        check(random_three_sat(rng))

    # a few larger random ones
    for _ in range(60):
        check(random_three_sat(rng, max_vars=6, max_clauses=6))

    # explicit edge cases
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
