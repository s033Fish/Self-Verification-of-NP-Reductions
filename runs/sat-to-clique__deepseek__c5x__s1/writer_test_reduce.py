"""Brute-force solvers and tests for the SAT -> Clique reduction."""

from __future__ import annotations

import itertools
import random

from problems import Sat, Clique
from reduce import reduce


# ---------------------------------------------------------------- solvers

def sat_solve(instance: dict) -> bool:
    """Brute force SAT: try every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {v: bits[v - 1] for v in range(1, m + 1)}
        ok = True
        for clause in clauses:
            if not any(
                (assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def clique_solve(instance: dict) -> bool:
    """Brute force Clique: does the graph have a clique of size >= k?"""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    for combo in itertools.combinations(range(n), k):
        if all(b in adj[a] for a, b in itertools.combinations(combo, 2)):
            return True
    return False


# ---------------------------------------------------------------- tests

def check(instance: dict) -> None:
    Sat.validate(instance)
    out = reduce(instance)
    Clique.validate(out)
    expected = sat_solve(instance)
    got = clique_solve(out)
    assert expected == got, (
        f"MISMATCH for {instance}: sat={expected}, clique={got}, reduced={out}"
    )


def all_small_instances():
    """Enumerate many small SAT instances."""
    # num_vars 0..3, clauses built from literals over those vars.
    for m in range(0, 4):
        literals = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
        # all clauses of size 0..2 (including duplicates/contradictions)
        clause_pool = [[]]
        for size in (1, 2):
            clause_pool += [list(c) for c in itertools.product(literals, repeat=size)]
        # formulas with 0..2 clauses
        for num_clauses in range(0, 3):
            for clauses in itertools.product(clause_pool, repeat=num_clauses):
                yield {"num_vars": m, "clauses": [list(c) for c in clauses]}


def test_exhaustive_small():
    count = 0
    for instance in all_small_instances():
        check(instance)
        count += 1
    return count


def test_edge_cases():
    cases = [
        {"num_vars": 0, "clauses": []},                       # no clauses -> yes
        {"num_vars": 0, "clauses": [[]]},                     # empty clause -> no
        {"num_vars": 1, "clauses": [[1]]},                    # yes
        {"num_vars": 1, "clauses": [[-1]]},                   # yes
        {"num_vars": 1, "clauses": [[1], [-1]]},              # no
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]},       # yes
        {"num_vars": 2, "clauses": [[1], [2], [-1, -2]]},     # no
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2], [-3]]},  # yes
        {"num_vars": 2, "clauses": [[1, 1], [1, -1]]},        # yes (repeat/contradiction)
        {"num_vars": 2, "clauses": [[1, -1], [-1, 1]]},       # yes
    ]
    for instance in cases:
        check(instance)
    return len(cases)


def test_random():
    rng = random.Random(12345)
    count = 0
    for _ in range(2000):
        m = rng.randint(0, 5)
        literals = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
        num_clauses = rng.randint(0, 5)
        clauses = []
        for _ in range(num_clauses):
            size = rng.randint(0, 3)
            if not literals:
                clauses.append([])
            else:
                clauses.append([rng.choice(literals) for _ in range(size)])
        check({"num_vars": m, "clauses": clauses})
        count += 1
    return count


def main():
    tests_run = 0
    tests_passed = 0
    for name, fn in [
        ("exhaustive_small", test_exhaustive_small),
        ("edge_cases", test_edge_cases),
        ("random", test_random),
    ]:
        tests_run += 1
        try:
            n = fn()
            tests_passed += 1
            print(f"PASS {name} ({n} instances)")
        except AssertionError as exc:
            print(f"FAIL {name}: {exc}")
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
