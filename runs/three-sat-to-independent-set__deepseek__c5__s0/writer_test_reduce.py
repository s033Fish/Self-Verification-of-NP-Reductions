"""Brute-force solvers and randomized tests for the 3-SAT -> IS reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions in problems.py.

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {v + 1: bits[v] for v in range(m)}
        if all(
            any((lit > 0) == assignment[abs(lit)] for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_independent_set(instance):
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
            if all(frozenset(e) - s for e in edge_set):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def random_three_sat(rng, max_vars=5, max_clauses=5):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            variables = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in variables]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustively enumerate small formulas with m <= 3 and <= 2 clauses."""
    instances = []
    for m in range(0, 4):
        if m < 3:
            instances.append({"num_vars": m, "clauses": []})
            continue
        literals = [l for v in range(1, m + 1) for l in (v, -v)]
        possible = []
        for combo in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                possible.append([s * v for s, v in zip(signs, combo)])
        instances.append({"num_vars": m, "clauses": []})
        for clause in possible:
            instances.append({"num_vars": m, "clauses": [clause]})
        for c1, c2 in itertools.combinations(possible, 2):
            instances.append({"num_vars": m, "clauses": [c1, c2]})
    return instances


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    instances = all_small_three_sat()
    instances += [random_three_sat(rng) for _ in range(3000)]

    for inst in instances:
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        IndependentSet.validate(reduced)
        expected = solve_three_sat(inst)
        got = solve_independent_set(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", reduced, "expected", expected, "got", got)

    # Explicit edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4], [1, -2, -4]]},
    ]
    for inst in edge_cases:
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        IndependentSet.validate(reduced)
        expected = solve_three_sat(inst)
        got = solve_independent_set(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("EDGE MISMATCH", inst, "->", reduced, "expected", expected, "got", got)

    # Larger randomized stress test with more variables and clauses.
    for _ in range(2000):
        m = rng.randint(3, 7)
        nclauses = rng.randint(0, 8)
        clauses = []
        for _ in range(nclauses):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        inst = {"num_vars": m, "clauses": clauses}
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        IndependentSet.validate(reduced)
        expected = solve_three_sat(inst)
        got = solve_independent_set(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("STRESS MISMATCH", inst, "->", reduced, "expected", expected, "got", got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_passed == tests_run, "some tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
