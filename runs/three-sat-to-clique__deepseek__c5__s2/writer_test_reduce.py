"""Brute-force solvers for both problems and tests for the reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the definitions in problems.py)

def solve_three_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance: dict) -> bool:
    """Yes iff there is a clique of size >= k."""
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
        if all(adj[u][v] for u, v in itertools.combinations(combo, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, valid instances)

def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 5):
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
    """Exhaustively enumerate small formulas."""
    instances = []
    # no clauses, various m
    for m in range(0, 4):
        instances.append({"num_vars": m, "clauses": []})
    # m = 3, all clauses over 3 vars (sign patterns), subsets of size 0..2
    var_triples = [[1, 2, 3]]
    all_clauses = []
    for triple in var_triples:
        for signs in itertools.product([1, -1], repeat=3):
            all_clauses.append([s * v for s, v in zip(signs, triple)])
    # also clauses over vars {1,2,4} with m=4
    for triple in [[1, 2, 4]]:
        for signs in itertools.product([1, -1], repeat=3):
            all_clauses.append([s * v for s, v in zip(signs, triple)])
    for size in range(0, 3):
        for combo in itertools.combinations(all_clauses, size):
            instances.append({"num_vars": 4, "clauses": [list(c) for c in combo]})
    return instances


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(src, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(src)
        tgt = reduce(src)
        Clique.validate(tgt)
        a = solve_three_sat(src)
        b = solve_clique(tgt)
        if a == b:
            tests_passed += 1
        else:
            failures.append((label, src, tgt, a, b))

    # Edge cases
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "empty m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]},
          "three clauses")
    # duplicate clauses
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate")

    # Exhaustive small
    for src in all_small_three_sat():
        check(src, "exhaustive")

    # Random
    rng = random.Random(12345)
    for _ in range(400):
        check(random_three_sat(rng), "random")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for f in failures[:5]:
        print("FAILURE:", f)

    verified = tests_passed == tests_run
    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
    print("verdict.json:", {"verified": verified, "tests_run": tests_run,
                            "tests_passed": tests_passed})
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
