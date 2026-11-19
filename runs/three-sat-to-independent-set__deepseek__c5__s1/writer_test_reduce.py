"""Tests for the 3-SAT -> Independent Set reduction.

Includes brute-force solvers written from the problem definitions, and
randomized/exhaustive comparisons on small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the definitions; not used by reduce).

def solve_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
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
    edge_set = {frozenset(e) for e in edges}
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(frozenset(e) not in edge_set or not (e[0] in s and e[1] in s)
                   for e in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Test helpers.

def random_three_sat(rng: random.Random, max_vars: int, max_clauses: int) -> dict:
    m = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    if num_clauses > 0:
        m = max(m, 3)
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(instance)
        reduced = reduce(instance)
        IndependentSet.validate(reduced)
        expected = solve_three_sat(instance)
        got = solve_independent_set(reduced)
        assert expected == got, (
            f"mismatch: source={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )
        tests_passed += 1

    # Hand-picked edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3], [1, 2, 3]]})
    # Duplicate clauses.
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    # Unsatisfiable small formula (all 8 clauses over 3 vars).
    all_clauses = [
        [a, b, c]
        for a in (1, -1) for b in (2, -2) for c in (3, -3)
    ]
    check({"num_vars": 3, "clauses": all_clauses})

    # Exhaustive-ish random testing.
    for _ in range(400):
        check(random_three_sat(rng, max_vars=6, max_clauses=5))

    # Larger random instances (still brute-forceable).
    for _ in range(40):
        check(random_three_sat(rng, max_vars=8, max_clauses=6))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
