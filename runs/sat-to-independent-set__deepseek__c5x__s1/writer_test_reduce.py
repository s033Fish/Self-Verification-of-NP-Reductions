"""Tests for reduce.py: compare brute-force answers on small SAT instances."""

from __future__ import annotations

import itertools
import random

from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_solve(instance: dict) -> bool:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        assignment = {v: bits[v - 1] for v in range(1, num_vars + 1)}
        ok = True
        for clause in clauses:
            if not any(
                (literal > 0 and assignment[literal]) or
                (literal < 0 and not assignment[-literal])
                for literal in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_solve(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(not (adjacency[u] & chosen) for u in chosen):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, including edge cases).

def random_sat_instance(rng: random.Random, max_vars: int = 4, max_clauses: int = 4,
                        max_len: int = 3, allow_empty_clause: bool = True) -> dict:
    num_vars = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, max_len)
        if length == 0 and not allow_empty_clause:
            length = 1
        if num_vars == 0:
            clause = []
        else:
            clause = []
            for _ in range(length):
                var = rng.randint(1, num_vars)
                clause.append(var if rng.random() < 0.5 else -var)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def handcrafted_instances() -> list[dict]:
    return [
        {"num_vars": 0, "clauses": []},                       # yes (no clauses)
        {"num_vars": 0, "clauses": [[]]},                     # no (empty clause)
        {"num_vars": 1, "clauses": [[1]]},                    # yes
        {"num_vars": 1, "clauses": [[-1]]},                   # yes
        {"num_vars": 1, "clauses": [[1], [-1]]},              # no
        {"num_vars": 2, "clauses": [[1, 2], [-1, -2]]},       # yes
        {"num_vars": 2, "clauses": [[1], [-1], [2]]},         # no
        {"num_vars": 2, "clauses": [[1, 1], [1, 1]]},         # yes (dupes)
        {"num_vars": 2, "clauses": [[1, -1]]},                # yes (tautology)
        {"num_vars": 3, "clauses": [[1, 2], [2, 3], [-1, -3]]},  # yes
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1], [-2], [-3]]},  # no
        {"num_vars": 4, "clauses": [[1, 2], [3, 4], [-1, -3], [-2, -4]]},  # yes
        {"num_vars": 2, "clauses": [[1], [1], [1]]},          # yes
        {"num_vars": 3, "clauses": [[1, -2], [-1, 2], [3], [-3]]},  # no
    ]


# ----------------------------------------------------------------------
# Test driver.

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
        got = independent_set_solve(reduced)
        if expected != got:
            raise AssertionError(
                f"mismatch: source={instance} expected={expected} "
                f"reduced={reduced} got={got}"
            )
        tests_passed += 1

    for instance in handcrafted_instances():
        check(instance)

    rng = random.Random(12345)
    for _ in range(3000):
        check(random_sat_instance(rng))

    # A few slightly larger random instances.
    for _ in range(200):
        check(random_sat_instance(rng, max_vars=5, max_clauses=6, max_len=4))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
