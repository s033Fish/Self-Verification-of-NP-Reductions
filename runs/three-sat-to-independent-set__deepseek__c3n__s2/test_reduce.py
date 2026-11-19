"""Tests for the 3-SAT -> Independent Set reduction.

Contains brute-force solvers for both problems (written from the
definitions in problems.py) and compares answers on many small random
source instances plus the documented edge cases.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def solve_three_sat(instance: dict) -> bool:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # variable v (1..num_vars) is bits[v-1]
        ok = True
        for clause in clauses:
            if not any(
                (lit > 0 and bits[lit - 1]) or (lit < 0 and not bits[-lit - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance: dict) -> bool:
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
    # brute force over all subsets of size >= k (check maximal sizes)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(not (adj[u] & s) for u in subset):
                return True
    return False


# ----------------------------------------------------------------------
# Helpers


def random_three_sat(rng: random.Random, max_vars: int = 4, max_clauses: int = 5) -> dict:
    num_vars = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    if num_vars >= 3:
        for _ in range(num_clauses):
            variables = rng.sample(range(1, num_vars + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in variables]
            clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def check_instance(instance: dict) -> bool:
    ThreeSat.validate(instance)
    target = reduce(instance)
    IndependentSet.validate(target)
    expected = solve_three_sat(instance)
    got = solve_independent_set(target)
    assert expected == got, (instance, target, expected, got)
    return expected


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check_instance(instance)
        tests_passed += 1

    # Documented edge cases.
    run({"num_vars": 0, "clauses": []})
    run({"num_vars": 3, "clauses": []})
    run({"num_vars": 5, "clauses": []})
    # Unsatisfiable: all 8 clauses over 3 vars.
    all_clauses = [
        [a, b, c]
        for a in (1, -1)
        for b in (2, -2)
        for c in (3, -3)
    ]
    run({"num_vars": 3, "clauses": all_clauses})
    # Duplicate clauses.
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    # Unused variables.
    run({"num_vars": 6, "clauses": [[1, 2, 3]]})
    # Simple satisfiable / unsatisfiable.
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3]]})

    # Exhaustive-ish random testing.
    rng = random.Random(12345)
    for _ in range(4000):
        run(random_three_sat(rng))

    # A few larger random instances (still brute-forceable).
    for _ in range(200):
        run(random_three_sat(rng, max_vars=6, max_clauses=8))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": tests_run == tests_passed, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
