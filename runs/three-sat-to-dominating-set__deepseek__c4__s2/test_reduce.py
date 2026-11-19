"""Tests for the 3-SAT -> Dominating Set reduction.

Includes brute-force solvers written directly from the problem definitions,
plus randomized comparisons on many small instances and hand-picked edge
cases.
"""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from problems import ThreeSat, DominatingSet


# ----------------------------------------------------------------------
# Solvers (from the definitions in problems.py)

def solve_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(
            any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_dominating_set(instance: dict) -> bool:
    """Exact dominating set via branch and bound; handles moderate sizes."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True

    closed = [1 << i for i in range(n)]
    for u, v in edges:
        closed[u] |= 1 << v
        closed[v] |= 1 << u
    full = (1 << n) - 1

    def rec(dominated: int, budget: int) -> bool:
        if dominated == full:
            return True
        if budget == 0:
            return False
        # pick an undominated vertex
        undom = (~dominated) & full
        v = (undom & -undom).bit_length() - 1
        # candidates: v and its neighbours
        cand = closed[v]
        # try including each candidate
        c = cand
        while c:
            b = c & -c
            idx = b.bit_length() - 1
            if rec(dominated | closed[idx], budget - 1):
                return True
            c ^= b
        return False

    return rec(0, k)


# ----------------------------------------------------------------------
# Instance generators

def random_three_sat(rng, max_vars=4, max_clauses=2):
    m = rng.randint(0, max_vars)
    if m < 3:
        clauses = []
    else:
        q = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(q):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests

def check(instance: dict) -> None:
    ThreeSat.validate(instance)
    out = reduce(instance)
    DominatingSet.validate(out)
    expected = solve_three_sat(instance)
    got = solve_dominating_set(out)
    assert got == expected, (
        f"mismatch on {instance}: expected {expected}, got {got}, reduction {out}"
    )


def test_edge_cases() -> None:
    cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4], [1, -2, -4], [-3, 2, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3],
                                    [1, 2, 3], [-1, -2, -3]]},
    ]
    for inst in cases:
        check(inst)


def test_all_clauses_unsat() -> None:
    """The 8-clause formula over 3 vars is unsatisfiable."""
    clauses = [[s[i] * (i + 1) for i in range(3)]
               for s in itertools.product([1, -1], repeat=3)]
    inst = {"num_vars": 3, "clauses": clauses}
    assert solve_three_sat(inst) is False
    out = reduce(inst)
    DominatingSet.validate(out)
    assert solve_dominating_set(out) is False


def test_random() -> int:
    rng = random.Random(12345)
    count = 0
    for _ in range(800):
        check(random_three_sat(rng, max_vars=4, max_clauses=2))
        count += 1
    for _ in range(300):
        check(random_three_sat(rng, max_vars=3, max_clauses=3))
        count += 1
    for _ in range(200):
        check(random_three_sat(rng, max_vars=5, max_clauses=4))
        count += 1
    return count


def test_exhaustive_small() -> int:
    """Exhaustively test all formulas with m=3 and up to 3 clauses."""
    count = 0
    possible_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        possible_clauses.append([signs[i] * (i + 1) for i in range(3)])
    for q in range(0, 4):
        for clauses in itertools.combinations_with_replacement(possible_clauses, q):
            check({"num_vars": 3, "clauses": [list(c) for c in clauses]})
            count += 1
    return count


def test_poly_size() -> int:
    rng = random.Random(999)
    count = 0
    for _ in range(50):
        m = rng.randint(3, 12)
        q = rng.randint(0, 10)
        clauses = []
        for _ in range(q):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        inst = {"num_vars": m, "clauses": clauses}
        ThreeSat.validate(inst)
        out = reduce(inst)
        DominatingSet.validate(out)
        assert out["n"] == 3 * m + 3 * q
        assert out["k"] == m + q
        count += 1
    return count


if __name__ == "__main__":
    tests_run = 0
    tests_passed = 0

    test_edge_cases(); tests_run += 1; tests_passed += 1
    test_all_clauses_unsat(); tests_run += 1; tests_passed += 1
    n = test_random(); tests_run += n; tests_passed += n
    n = test_exhaustive_small(); tests_run += n; tests_passed += n
    n = test_poly_size(); tests_run += n; tests_passed += n

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": tests_passed == tests_run,
                   "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)
    print(f"all tests passed: {tests_passed}/{tests_run}")
