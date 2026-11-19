"""Tests for the 3-SAT -> Vertex Cover reduction in reduce.py.

Includes independent brute-force solvers for both problems (problems.py has
none) and compares them on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeSat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(
            any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def _maximal_matching_size(edges, alive):
    """Greedy maximal matching size (a lower bound on min vertex cover)."""
    used = set()
    size = 0
    for u, v in edges:
        if u in alive and v in alive and u not in used and v not in used:
            used.add(u)
            used.add(v)
            size += 1
    return size


def solve_vertex_cover(instance: dict) -> bool:
    """Exact decision procedure via branch and bound."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True

    def rec(alive, budget):
        # alive: set of vertices still allowed to be chosen.
        remaining = [(u, v) for u, v in edges if u in alive and v in alive]
        if not remaining:
            return True
        if budget < 0:
            return False
        if _maximal_matching_size(remaining, alive) > budget:
            return False
        u, v = remaining[0]
        for pick in (u, v):
            if rec(alive - {pick}, budget - 1):
                return True
        return False

    return rec(set(range(n)), k)


# ----------------------------------------------------------------------
# Test bookkeeping.

TESTS_RUN = 0
TESTS_PASSED = 0


def check(condition: bool, message: str) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    if condition:
        TESTS_PASSED += 1
    else:
        raise AssertionError(message)


def check_reduction(instance: dict) -> None:
    ThreeSat.validate(instance)
    target = reduce(instance)
    VertexCover.validate(target)
    expected = solve_three_sat(instance)
    got = solve_vertex_cover(target)
    check(
        expected == got,
        f"mismatch on {instance}: source={expected}, reduced={got}, target={target}",
    )


# ----------------------------------------------------------------------
# Edge cases.

def test_edge_cases() -> None:
    check_reduction({"num_vars": 0, "clauses": []})
    for m in range(0, 6):
        check_reduction({"num_vars": m, "clauses": []})
    check_reduction({"num_vars": 3, "clauses": [[1, 2, 3]]})
    all_clauses = [[a, b, c] for a in (1, -1) for b in (2, -2) for c in (3, -3)]
    check_reduction({"num_vars": 3, "clauses": all_clauses})
    check_reduction({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check_reduction({"num_vars": 5, "clauses": [[1, 2, 3]]})
    check_reduction(
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]}
    )
    # Unsatisfiable 2-variable-ish style over 3 vars, all negations.
    check_reduction({"num_vars": 3, "clauses": [[-1, -2, -3], [1, 2, 3]]})


# ----------------------------------------------------------------------
# Randomized testing.

def random_instance(rng: random.Random, max_vars: int = 5, max_clauses: int = 6) -> dict:
    m = rng.randint(3, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        variables = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def test_random() -> None:
    rng = random.Random(12345)
    for _ in range(400):
        check_reduction(random_instance(rng))


def test_reduction_shape() -> None:
    instance = {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}
    target = reduce(instance)
    check(target["n"] == 2 * 3 + 3 * 2, "wrong vertex count")
    check(target["k"] == 3 + 2 * 2, "wrong k")
    seen = set()
    for u, v in target["edges"]:
        check(u != v, "self loop")
        key = frozenset((u, v))
        check(key not in seen, "duplicate edge")
        seen.add(key)


def main() -> None:
    test_edge_cases()
    test_reduction_shape()
    test_random()
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": TESTS_RUN, "tests_passed": TESTS_PASSED},
            fh,
        )


if __name__ == "__main__":
    main()
