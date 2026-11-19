"""Tests for the NAE-3-SAT -> 3-Coloring reduction.

Brute-force solvers for both problems are implemented here from the
definitions in problems.py, then compared on many small instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers


def solve_nae3sat(instance: dict) -> bool:
    """Brute force: try every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            values = []
            for literal in clause:
                value = bits[abs(literal) - 1]
                values.append(value if literal > 0 else not value)
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_three_coloring(instance: dict) -> bool:
    """Exact backtracking search for a proper 3-colouring."""
    n = instance["n"]
    edges = instance["edges"]
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    colours = [-1] * n

    def backtrack(vertex: int) -> bool:
        if vertex == n:
            return True
        used = {colours[w] for w in adj[vertex] if colours[w] != -1}
        for colour in range(3):
            if colour not in used:
                colours[vertex] = colour
                if backtrack(vertex + 1):
                    return True
                colours[vertex] = -1
        return False

    return backtrack(0)


# ----------------------------------------------------------------------
# Instance generation


def random_nae_instance(rng: random.Random, max_vars: int, max_clauses: int) -> dict:
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            variables = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in variables]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_instances(max_vars: int = 4):
    """Exhaustively enumerate small NAE-3-SAT instances (m <= max_vars)."""
    for m in range(0, max_vars + 1):
        if m < 3:
            yield {"num_vars": m, "clauses": []}
            continue
        variable_triples = list(itertools.combinations(range(1, m + 1), 3))
        sign_choices = list(itertools.product((1, -1), repeat=3))
        # all possible clauses (with order fixed by sorted variables)
        possible_clauses = []
        for triple in variable_triples:
            for signs in sign_choices:
                possible_clauses.append([s * v for s, v in zip(signs, triple)])
        # all subsets of clauses up to size 3 (keeps the count manageable)
        for size in range(0, 3):
            for combo in itertools.combinations(possible_clauses, size):
                yield {"num_vars": m, "clauses": [list(c) for c in combo]}


# ----------------------------------------------------------------------
# Tests


def check(instance: dict, count: list) -> None:
    problems.SOURCE.validate(instance)
    reduced = reduce(instance)
    problems.TARGET.validate(reduced)
    expected = solve_nae3sat(instance)
    got = solve_three_coloring(reduced)
    count[0] += 1
    assert expected == got, (
        f"mismatch on {instance}: source={expected}, target={got}, "
        f"reduced={reduced}"
    )
    count[1] += 1


def main() -> None:
    count = [0, 0]  # [tests_run, tests_passed]

    # 1. Edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]},
    ]
    for instance in edge_cases:
        check(instance, count)

    # 2. Exhaustive small instances.
    for instance in all_small_instances(max_vars=4):
        check(instance, count)

    # 3. Random instances.
    rng = random.Random(12345)
    for _ in range(3000):
        instance = random_nae_instance(rng, max_vars=6, max_clauses=8)
        check(instance, count)

    print(f"tests_run={count[0]} tests_passed={count[1]}")

    import json

    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": count[0] == count[1],
                "tests_run": count[0],
                "tests_passed": count[1],
            },
            fh,
        )


if __name__ == "__main__":
    main()
