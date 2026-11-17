"""Tests for the Clique -> Independent Set reduction.

problems.py has no solvers, so we implement brute-force solvers for both
problems from the definitions and compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def _has_clique(n, edges, k):
    """Yes iff graph has a clique of at least k vertices."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for subset in itertools.combinations(range(n), k):
        ok = True
        for a, b in itertools.combinations(subset, 2):
            if not adj[a][b]:
                ok = False
                break
        if ok:
            return True
    return False


def _has_independent_set(n, edges, k):
    """Yes iff graph has an independent set of at least k vertices."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for subset in itertools.combinations(range(n), k):
        ok = True
        for a, b in itertools.combinations(subset, 2):
            if adj[a][b]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance):
    return _has_clique(instance["n"], instance["edges"], instance["k"])


def solve_independent_set(instance):
    return _has_independent_set(instance["n"], instance["edges"], instance["k"])


# ----------------------------------------------------------------------
# Test harness.

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1

    Clique.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)

    expected = solve_clique(instance)
    got = solve_independent_set(reduced)
    assert got == expected, (
        f"mismatch on {instance!r}: clique={expected}, "
        f"reduced={reduced!r}, indep={got}"
    )
    tests_passed += 1


def all_graphs(n):
    """Yield every simple undirected graph on n vertices as an edge list."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]


def main():
    # Exhaustive: all graphs for n = 0..5, all relevant k values.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    # Specific edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": -5})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]], "k": 3})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]], "k": 4})
    check({"n": 5, "edges": [], "k": 5})          # no edges: IS yes, clique no
    check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2],
                             [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]], "k": 5})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
