"""Tests for reduce.py: brute-force solvers for both problems and comparison."""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)

def solve_exact_cover(instance: dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # Try every subset of the available sets.
    for mask in range(1 << n):
        covered = [False] * u
        ok = True
        for i in range(n):
            if mask & (1 << i):
                for e in sets[i]:
                    if covered[e]:
                        ok = False
                        break
                    covered[e] = True
                if not ok:
                    break
        if ok and all(covered):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assignment = [(bits >> (v - 1)) & 1 == 1 for v in range(1, m + 1)]
        if all(
            any(
                (lit > 0 and assignment[lit - 1]) or (lit < 0 and not assignment[-lit - 1])
                for lit in clause
            )
            for clause in clauses
        ):
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def random_exact_cover(rng: random.Random, max_u: int = 4, max_sets: int = 5) -> dict:
    u = rng.randint(0, max_u)
    n = rng.randint(0, max_sets)
    sets = []
    for _ in range(n):
        size = rng.randint(0, u)
        subset = rng.sample(range(u), size) if u else []
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def random_sat(rng: random.Random, max_vars: int = 4, max_clauses: int = 5) -> dict:
    m = rng.randint(0, max_vars)
    n = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(n):
        length = rng.randint(0, 3)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def check_reduction(instance: dict) -> bool:
    """Validate both instances and check the answers agree."""
    ExactCover.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    return solve_exact_cover(instance) == solve_sat(out)


# ----------------------------------------------------------------------
# Tests

def test_solvers_sanity() -> None:
    # Exact cover edge cases
    assert solve_exact_cover({"universe_size": 0, "sets": []}) is True
    assert solve_exact_cover({"universe_size": 0, "sets": [[], []]}) is True
    assert solve_exact_cover({"universe_size": 1, "sets": []}) is False
    assert solve_exact_cover({"universe_size": 1, "sets": [[0], [0]]}) is True
    assert solve_exact_cover({"universe_size": 2, "sets": [[0], [0], [1]]}) is True
    assert solve_exact_cover({"universe_size": 2, "sets": [[0, 1], [1]]}) is True
    assert solve_exact_cover({"universe_size": 2, "sets": [[0], [1]]}) is True
    assert solve_exact_cover({"universe_size": 2, "sets": [[0]]}) is False
    # SAT edge cases
    assert solve_sat({"num_vars": 0, "clauses": []}) is True
    assert solve_sat({"num_vars": 0, "clauses": [[]]}) is False
    assert solve_sat({"num_vars": 1, "clauses": [[1], [-1]]}) is False
    assert solve_sat({"num_vars": 1, "clauses": [[1], [1]]}) is True
    assert solve_sat({"num_vars": 2, "clauses": [[1, 2], [-1], [-2]]}) is False


def test_hand_cases() -> None:
    cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[]]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0, 1, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2]]},
        {"universe_size": 3, "sets": [[0], [1], [2], [0, 1, 2]]},
        {"universe_size": 3, "sets": [[0, 1], [2], [0], [1, 2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
        {"universe_size": 4, "sets": [[0, 1], [1, 2], [2, 3], [3, 0]]},
    ]
    for case in cases:
        assert check_reduction(case), case


def test_random_exhaustive() -> None:
    rng = random.Random(12345)
    count = 0
    for _ in range(3000):
        inst = random_exact_cover(rng)
        assert check_reduction(inst), inst
        count += 1
    print(f"random exhaustive cases passed: {count}")


def test_duplicates_and_empties() -> None:
    rng = random.Random(999)
    for _ in range(1000):
        u = rng.randint(0, 3)
        base = []
        for _ in range(rng.randint(0, 3)):
            base.append(rng.sample(range(u), rng.randint(0, u)) if u else [])
        sets = base + base + [[] for _ in range(rng.randint(0, 2))]
        inst = {"universe_size": u, "sets": sets}
        assert check_reduction(inst), inst


if __name__ == "__main__":
    test_solvers_sanity()
    test_hand_cases()
    test_random_exhaustive()
    test_duplicates_and_empties()
    print("ALL TESTS PASSED")
