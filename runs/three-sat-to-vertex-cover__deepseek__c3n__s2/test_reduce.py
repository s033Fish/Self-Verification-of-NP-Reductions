"""Tests for reduce.py: brute-force solvers + randomized comparison."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_sat(instance: dict) -> bool:
    """Try every assignment of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                   for l in clause) for clause in clauses):
            return True
    return False


def solve_vertex_cover(instance: dict) -> bool:
    """Exact branch-and-bound: is there a cover of size <= k?

    Repeatedly pick an uncovered edge and branch on including one of its
    endpoints, tracking the remaining budget.  This is exhaustive and
    correct, just pruned.
    """
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True

    def rec(chosen: frozenset, budget: int) -> bool:
        if budget < 0:
            return False
        for u, v in edges:
            if u not in chosen and v not in chosen:
                # branch on this uncovered edge
                return (rec(chosen | {u}, budget - 1)
                        or rec(chosen | {v}, budget - 1))
        return True

    return rec(frozenset(), k)


# ----------------------------------------------------------------------
# Instance generators for small 3-SAT formulas.

def random_three_sat(rng: random.Random, max_vars: int = 4,
                     max_clauses: int = 4) -> dict:
    m = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    if m < 3:
        num_clauses = 0  # clauses need m >= 3
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustive small formulas over variables 1..3."""
    yield {"num_vars": 0, "clauses": []}
    yield {"num_vars": 1, "clauses": []}
    yield {"num_vars": 2, "clauses": []}
    sign_patterns = list(itertools.product([1, -1], repeat=3))
    all_clauses = [[s * v for s, v in zip(signs, (1, 2, 3))]
                   for signs in sign_patterns]
    for r in range(0, 4):
        for combo in itertools.combinations(all_clauses, r):
            yield {"num_vars": 3, "clauses": [list(c) for c in combo]}
    for c in all_clauses:
        yield {"num_vars": 3, "clauses": [list(c), list(c)]}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(instance)
        expected = solve_three_sat(instance)
        reduced = reduce(instance)
        VertexCover.validate(reduced)
        got = solve_vertex_cover(reduced)
        assert got == expected, (
            f"mismatch: instance={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )
        tests_passed += 1

    for instance in all_small_three_sat():
        check(instance)

    rng = random.Random(12345)
    for _ in range(5000):
        check(random_three_sat(rng, max_vars=4, max_clauses=4))

    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3],
                                      [1, 2, -3], [-1, -2, -3]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
