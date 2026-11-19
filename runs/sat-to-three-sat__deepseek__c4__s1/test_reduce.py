"""Tests for the SAT -> 3-SAT reduction.

Brute-force solvers are written directly from the problem definitions, then
many small random source instances are reduced and the answers compared.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


def sat_solve(instance) -> bool:
    """Brute force SAT solver from the definition."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        def val(lit):
            v = bits[abs(lit) - 1]
            return v if lit > 0 else not v
        if all(any(val(l) for l in c) for c in clauses):
            return True
    return False


def three_sat_solve(instance) -> bool:
    """Brute force 3-SAT solver from the definition."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        def val(lit):
            v = bits[abs(lit) - 1]
            return v if lit > 0 else not v
        if all(any(val(l) for l in c) for c in clauses):
            return True
    return False


def random_instance(rng, max_vars=4, max_clauses=5, max_len=4):
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


def check(instance):
    problems.Sat.validate(instance)
    reduced = reduce(instance)
    problems.ThreeSat.validate(reduced)
    expected = sat_solve(instance)
    got = three_sat_solve(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    def run(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Explicit edge cases.
    run({"num_vars": 0, "clauses": []})
    run({"num_vars": 0, "clauses": [[]]})
    run({"num_vars": 3, "clauses": []})
    run({"num_vars": 1, "clauses": [[1]]})
    run({"num_vars": 1, "clauses": [[-1]]})
    run({"num_vars": 1, "clauses": [[1], [-1]]})
    run({"num_vars": 2, "clauses": [[1, 2], [-1, -2]]})
    run({"num_vars": 2, "clauses": [[1, -1]]})          # tautology
    run({"num_vars": 2, "clauses": [[1, 1, -2]]})       # repeats
    run({"num_vars": 3, "clauses": [[1, 2, 3]]})
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    run({"num_vars": 4, "clauses": [[1, 2, 3, 4]]})
    run({"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1, -2, -3, -4]]})
    run({"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]})
    run({"num_vars": 5, "clauses": [[1, 2, 3, 4, 5], [-1, -2, -3, -4, -5]]})
    run({"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6]]})
    run({"num_vars": 4, "clauses": [[1, 2], [3, 4], [-1, -3], [-2, -4]]})
    run({"num_vars": 4, "clauses": [[1], [2], [3], [4]]})
    run({"num_vars": 4, "clauses": [[1, 2, 3, 4], []]})  # empty clause -> no

    # Random small instances.
    rng = random.Random(12345)
    for _ in range(3000):
        run(random_instance(rng))

    # Larger random instances (still brute-forceable).
    for _ in range(200):
        run(random_instance(rng, max_vars=6, max_clauses=8, max_len=6))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
