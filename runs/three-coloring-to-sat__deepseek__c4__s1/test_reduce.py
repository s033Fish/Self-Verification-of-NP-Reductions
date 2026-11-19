"""Tests for the 3-Coloring -> SAT reduction.

Includes independent brute-force solvers for both problems and compares
their answers on many small source instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable (brute force over 3^n colourings)."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """True iff the CNF is satisfiable (brute force over 2^m assignments)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                       for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators.

def all_graphs(n: int):
    """Yield every simple undirected graph on n vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(rng: random.Random, n: int) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < 0.5:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.ThreeColoring.validate(instance)
        reduced = reduce(instance)
        problems.Sat.validate(reduced)
        expected = solve_three_coloring(instance)
        got = solve_sat(reduced)
        assert got == expected, (
            f"mismatch on {instance}: 3-color={expected}, sat={got}, "
            f"reduced={reduced}"
        )
        tests_passed += 1

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for graph in all_graphs(n):
            check(graph)

    # Random larger graphs (brute force SAT is 2^(3n), so keep n modest).
    rng = random.Random(12345)
    for _ in range(200):
        check(random_graph(rng, rng.randint(0, 6)))

    # Explicit edge cases from the docstrings.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    # K4 is not 3-colourable.
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})
    # K5 is not 3-colourable.
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]})
    # Odd cycle C5 is 3-colourable.
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})

    # The reduced SAT formula for an empty graph must be satisfiable.
    assert solve_sat(reduce({"n": 0, "edges": []})) is True
    tests_run += 1
    tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
