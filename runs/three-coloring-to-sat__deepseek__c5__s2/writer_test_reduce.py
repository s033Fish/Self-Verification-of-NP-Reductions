"""Tests for reduce.py: brute-force solvers for both problems plus a
randomized/exhaustive comparison of source answers with reduction answers."""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeColoring, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.
# ----------------------------------------------------------------------

def solve_three_coloring(instance) -> bool:
    """Try all 3^n colourings (n small in tests)."""
    n = instance["n"]
    edges = instance["edges"]
    for colours in itertools.product(range(3), repeat=n):
        if all(colours[u] != colours[v] for u, v in edges):
            return True
    return False


def solve_sat(instance) -> bool:
    """Try all 2^m assignments (m small in tests)."""
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
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n):
    """All simple graphs on vertices 0..n-1."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(rng, max_n=6):
    n = rng.randint(0, max_n)
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(p) for p in pairs if rng.random() < 0.4]
    return {"n": n, "edges": edges}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeColoring.validate(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        expected = solve_three_coloring(instance)
        got = solve_sat(reduced)
        assert expected == got, (
            f"mismatch on {instance}: source={expected}, reduced={got}, "
            f"reduction={reduced}"
        )
        tests_passed += 1

    # Exhaustive: every graph with up to 4 vertices.
    for n in range(0, 5):
        for graph in all_graphs(n):
            check(graph)

    # Hand-picked edge cases.
    check({"n": 0, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})          # K3: yes
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3],
                             [1, 2], [1, 3], [2, 3]]})          # K4: no
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4],
                             [4, 0], [0, 2]]})                  # 5-cycle + chord: no
    check({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})          # path: yes
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 0], [3, 4]]})  # K3 + edge: yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 0], [0, 3]]})  # K3 + pendant: yes

    # Random graphs, small enough to brute force.
    rng = random.Random(12345)
    for _ in range(300):
        check(random_graph(rng, max_n=6))
    for _ in range(40):
        check(random_graph(rng, max_n=7))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as fh:
        json.dump({"verified": True,
                   "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
        fh.write("\n")


if __name__ == "__main__":
    main()
