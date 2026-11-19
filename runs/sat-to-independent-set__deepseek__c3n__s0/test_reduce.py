"""Tests for reduce.py: compare brute-force answers on small SAT instances."""

from __future__ import annotations

import itertools
import random

from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_solve(instance: dict) -> bool:
    """Brute force SAT: try every assignment of variables 1..num_vars."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # bits[i] is the value of variable i+1
        ok = True
        for clause in clauses:
            if not any(
                (literal > 0) == bits[abs(literal) - 1] for literal in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def is_solve(instance: dict) -> bool:
    """Brute force Independent Set: is there an independent set of size >= k?"""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(v not in adj[u] for i, u in enumerate(subset) for v in subset[i + 1:]):
                return True
    return False


# ----------------------------------------------------------------------
# Hand-picked edge cases.

def edge_case_instances():
    return [
        {"num_vars": 0, "clauses": []},                       # yes
        {"num_vars": 1, "clauses": [[]]},                     # no (empty clause)
        {"num_vars": 3, "clauses": []},                       # yes
        {"num_vars": 1, "clauses": [[1], [-1]]},              # no
        {"num_vars": 1, "clauses": [[1, 1, 1]]},              # yes
        {"num_vars": 2, "clauses": [[1, -1]]},                # yes (tautology)
        {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2]]},  # yes
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2], [1, -2], [-1, 2]]},  # no
        {"num_vars": 3, "clauses": [[1], [2], [3]]},          # yes
        {"num_vars": 3, "clauses": [[1], [-1], [2]]},         # no
        {"num_vars": 4, "clauses": [[1, 2], [3, 4], [-1, -3]]},  # yes
    ]


def random_sat_instance(rng: random.Random) -> dict:
    num_vars = rng.randint(0, 5)
    num_clauses = rng.randint(0, 6)
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, 4)
        clause = []
        for _ in range(length):
            if num_vars == 0:
                break
            v = rng.randint(1, num_vars)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        Sat.validate(instance)
        reduced = reduce(instance)
        IndependentSet.validate(reduced)
        expected = sat_solve(instance)
        got = is_solve(reduced)
        if expected != got:
            raise AssertionError(
                f"MISMATCH source={instance} reduced={reduced} "
                f"sat={expected} is={got}"
            )
        tests_passed += 1

    # Edge cases.
    for instance in edge_case_instances():
        check(instance)

    # Random tests.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_sat_instance(rng))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
