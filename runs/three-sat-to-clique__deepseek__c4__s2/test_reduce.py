"""Tests for the 3-SAT -> Clique reduction, with independent brute-force solvers."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def sat_solve(instance: dict) -> bool:
    """Brute force 3-SAT: try every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {v: bits[v - 1] for v in range(1, m + 1)}
        if all(
            any(assignment[abs(l)] == (l > 0) for l in clause)
            for clause in clauses
        ):
            return True
    return False


def clique_solve(instance: dict) -> bool:
    """Brute force Clique: check all subsets of size k (and handle edge cases)."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edges = {frozenset(e) for e in instance["edges"]}
    for subset in itertools.combinations(range(n), k):
        if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators.

def random_3sat(rng: random.Random, max_vars: int = 6, max_clauses: int = 6) -> dict:
    m = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def exhaustive_small():
    """All formulas with up to 4 variables and up to 3 clauses over a small set."""
    for m in range(0, 5):
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        # build all possible clauses (ordered by variable, random sign)
        possible = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                possible.append([s * v for s, v in zip(signs, vs)])
        # sample subsets of clauses up to size 3
        for size in range(0, 4):
            for combo in itertools.combinations(possible, size):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = sat_solve(instance)
        reduced = reduce(instance)
        got = clique_solve(reduced)
        assert got == expected, (
            f"mismatch: source={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )
        tests_passed += 1

    # Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]})

    # Exhaustive small instances.
    for instance in exhaustive_small():
        check(instance)

    # Random instances.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_3sat(rng))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
