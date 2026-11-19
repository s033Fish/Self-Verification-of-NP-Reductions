"""Tests for the SAT -> Clique reduction in reduce.py.

Contains independent brute-force solvers for both problems (written straight
from the docstrings in problems.py) and compares them on many small source
instances against the reduction.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)

def sat_solve(instance):
    """Brute force SAT: try every assignment of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {v + 1: bits[v] for v in range(m)}
        ok = True
        for clause in clauses:
            if not any(
                (lit > 0 and assignment[lit]) or (lit < 0 and not assignment[-lit])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def clique_solve(instance):
    """Brute force Clique: look for a clique of size >= k."""
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
        if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def random_sat_instance(rng, max_vars=4, max_clauses=5, max_len=3):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_sat_instances():
    """Exhaustively enumerate small instances: m in 0..2, clauses over a pool."""
    pool = [1, -1, 2, -2]
    for m in range(0, 3):
        literals = [l for l in pool if abs(l) <= m]
        # all possible clauses (including empty) with up to 2 literals
        possible = [[]]
        for length in (1, 2):
            possible.extend([list(c) for c in itertools.combinations_with_replacement(literals, length)])
        # formulas with up to 3 clauses
        for num_clauses in range(0, 4):
            for combo in itertools.combinations_with_replacement(range(len(possible)), num_clauses):
                yield {"num_vars": m, "clauses": [list(possible[i]) for i in combo]}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        Sat.validate(instance)
        reduced = reduce(instance)
        Clique.validate(reduced)
        expected = sat_solve(instance)
        got = clique_solve(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((instance, reduced, expected, got))

    # 1. Exhaustive small instances
    for instance in all_small_sat_instances():
        check(instance)

    # 2. Random instances
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_sat_instance(rng, max_vars=4, max_clauses=5, max_len=3))

    # 3. Larger random instances (fewer, brute force still feasible)
    rng = random.Random(999)
    for _ in range(300):
        check(random_sat_instance(rng, max_vars=6, max_clauses=7, max_len=4))

    # 4. Targeted edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},                      # yes
        {"num_vars": 0, "clauses": [[]]},                    # no (empty clause)
        {"num_vars": 3, "clauses": []},                      # yes
        {"num_vars": 3, "clauses": [[]]},                    # no
        {"num_vars": 3, "clauses": [[1], [-1]]},             # no
        {"num_vars": 3, "clauses": [[1, -1]]},               # yes
        {"num_vars": 3, "clauses": [[1, 1, 1]]},             # yes
        {"num_vars": 3, "clauses": [[1, 2], [-1, -2]]},      # yes
        {"num_vars": 1, "clauses": [[1], [-1], [1]]},        # no
        {"num_vars": 2, "clauses": [[1, 2], [-1], [-2]]},    # no
        {"num_vars": 2, "clauses": [[1, 2], [-1, 2]]},       # yes
        {"num_vars": 4, "clauses": [[1, 2], [3, 4], [-1, -3]]},  # yes
    ]
    for instance in edge_cases:
        check(instance)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for instance, reduced, expected, got in failures[:10]:
            print("  instance:", instance)
            print("  reduced :", reduced)
            print("  expected:", expected, "got:", got)
        raise SystemExit(1)

    # Sanity: reduction must be polynomial-sized (rough upper bound check)
    big = {"num_vars": 20, "clauses": [[1, -2, 3], [2, 3, -4], [-1, 4], [5]]}
    r = reduce(big)
    assert r["k"] == 4
    assert r["n"] == sum(len(c) for c in big["clauses"])
    Clique.validate(r)
    print("all tests passed")


if __name__ == "__main__":
    main()
