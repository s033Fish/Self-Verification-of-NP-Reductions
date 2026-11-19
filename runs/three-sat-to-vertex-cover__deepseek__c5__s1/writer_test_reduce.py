"""Tests for the 3-SAT -> Vertex Cover reduction.

Includes brute-force solvers for both problems (from the definitions in
problems.py) and compares answers on many small source instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def solve_three_sat(instance: dict) -> bool:
    """Brute force over all assignments of variables 1..num_vars."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # bits[v-1] is the value of variable v
        if all(
            any((lit > 0) == bits[abs(lit) - 1] for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def min_vertex_cover_size(n: int, edges: list) -> int:
    """Exact minimum vertex cover size via edge branching (FPT in answer)."""
    best = n

    def rec(remaining, count):
        nonlocal best
        if count >= best:
            return
        if not remaining:
            best = count
            return
        u, v = remaining[0]
        # branch: include u, or include v
        rec([e for e in remaining if u != e[0] and u != e[1]], count + 1)
        rec([e for e in remaining if v != e[0] and v != e[1]], count + 1)

    rec(list(edges), 0)
    return best


def solve_vertex_cover(instance: dict) -> bool:
    """Yes iff a vertex cover of size at most k exists."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    return min_vertex_cover_size(n, edges) <= k


# ----------------------------------------------------------------------
# Instance generators (small, valid source instances)


def random_three_sat(rng: random.Random, max_vars: int = 4, max_clauses: int = 4) -> dict:
    num_vars = rng.randint(0, max_vars)
    if num_vars < 3:
        # clauses require at least 3 distinct variables
        return {"num_vars": num_vars, "clauses": []}
    n_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(n_clauses):
        variables = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def all_small_three_sat():
    """Exhaustively enumerate small valid 3-SAT instances."""
    for num_vars in range(0, 4):
        if num_vars < 3:
            yield {"num_vars": num_vars, "clauses": []}
            continue
        # all clauses over 3 distinct variables
        clauses = []
        for combo in itertools.combinations(range(1, num_vars + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                clauses.append([s * v for s, v in zip(signs, combo)])
        # all subsets of clauses up to size 3
        for r in range(0, 4):
            for chosen in itertools.combinations(clauses, r):
                yield {"num_vars": num_vars, "clauses": [list(c) for c in chosen]}


# ----------------------------------------------------------------------
# Tests


def check_instance(instance: dict) -> bool:
    """Return True if the reduction preserves the answer for this instance."""
    ThreeSat.validate(instance)
    target = reduce(instance)
    VertexCover.validate(target)
    expected = solve_three_sat(instance)
    got = solve_vertex_cover(target)
    if expected != got:
        print("MISMATCH")
        print("  source:", instance)
        print("  source answer:", expected)
        print("  target:", target)
        print("  target answer:", got)
        return False
    return True


def main() -> None:
    tests_run = 0
    tests_passed = 0

    # Exhaustive small instances
    for instance in all_small_three_sat():
        tests_run += 1
        if check_instance(instance):
            tests_passed += 1

    # Random instances
    rng = random.Random(12345)
    for _ in range(500):
        instance = random_three_sat(rng, max_vars=5, max_clauses=5)
        tests_run += 1
        if check_instance(instance):
            tests_passed += 1

    # Explicit edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 1, 2]]},
    ]
    for instance in edge_cases:
        tests_run += 1
        if check_instance(instance):
            tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
