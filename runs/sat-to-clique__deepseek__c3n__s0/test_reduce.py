"""Tests for reduce.py: SAT -> Clique.

Includes independent brute-force solvers for both problems (written from
the definitions, not using reduce) and compares answers on many small
instances plus hand-picked edge cases.
"""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from problems import Sat, Clique


# ----------------------------------------------------------------------
# Brute-force solvers (independent of the reduction)

def sat_solve(instance) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # variable v (1..m) -> bits[v-1]
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def clique_solve(instance) -> bool:
    """True iff the graph has a clique of at least k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for subset in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def check(instance):
    Sat.validate(instance)
    reduced = reduce(instance)
    Clique.validate(reduced)  # must be a valid target instance
    a = sat_solve(instance)
    b = clique_solve(reduced)
    assert a == b, f"mismatch: sat={a} clique={b}\ninput={instance}\nreduced={reduced}"
    return a


def random_sat(rng, max_vars=4, max_clauses=4, max_len=3):
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


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            check(instance)
            tests_passed += 1
        except AssertionError as exc:
            failures.append(f"{label}: {exc}")

    # Hand-picked edge cases.
    edge_cases = [
        ({"num_vars": 0, "clauses": []}, "no vars, no clauses"),
        ({"num_vars": 0, "clauses": [[]]}, "empty clause, no vars"),
        ({"num_vars": 3, "clauses": []}, "no clauses"),
        ({"num_vars": 3, "clauses": [[]]}, "one empty clause"),
        ({"num_vars": 1, "clauses": [[1]]}, "unit positive"),
        ({"num_vars": 1, "clauses": [[-1]]}, "unit negative"),
        ({"num_vars": 1, "clauses": [[1], [-1]]}, "contradiction"),
        ({"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2]]}, "3-clause sat"),
        ({"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]}, "unsat 2-var"),
        ({"num_vars": 3, "clauses": [[1, 1, 1]]}, "repeated literals"),
        ({"num_vars": 3, "clauses": [[1, -1]]}, "tautology"),
        ({"num_vars": 3, "clauses": [[1], [1], [1]]}, "repeated clause"),
        ({"num_vars": 3, "clauses": [[1, -1], []]}, "tautology plus empty"),
        ({"num_vars": 4, "clauses": [[1, 2], [3, 4], [-1, -3]]}, "mixed"),
    ]
    for inst, label in edge_cases:
        run(inst, label)

    # Exhaustive small formulas: all clause sets over up to 2 vars, clauses
    # drawn from a pool of small literal lists.
    pool = [[], [1], [-1], [2], [-2], [1, 2], [1, -2], [-1, 2], [-1, -2]]
    for m in (1, 2):
        p = [c for c in pool if all(abs(l) <= m for l in c)]
        for r in range(0, 4):
            for combo in itertools.combinations_with_replacement(p, r):
                run({"num_vars": m, "clauses": [list(c) for c in combo]},
                    f"exhaustive m={m} {combo}")

    # Randomized tests.
    rng = random.Random(12345)
    for _ in range(4000):
        run(random_sat(rng), "random")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for f in failures[:20]:
            print("FAIL:", f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
