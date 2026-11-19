"""Tests for the Clique -> Vertex Cover reduction.

Contains brute-force solvers for both problems (from the docstrings) and
compares their answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_clique(instance) -> bool:
    """Yes iff the graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False

    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    # A clique of size >= k exists iff some k-subset is a clique.
    for subset in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
            return True
    return False


def solve_vertex_cover(instance) -> bool:
    """Yes iff the graph has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True

    edges = [tuple(e) for e in edges]
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n):
    """Yield every simple undirected graph on n vertices as an edge list."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [[u, v] for i, (u, v) in enumerate(pairs) if (mask >> i) & 1]


def check(instance, label=""):
    reduced = reduce(instance)
    # Validate output shape.
    assert set(reduced) == {"n", "edges", "k"}, reduced
    assert reduced["n"] == instance["n"]
    assert reduced["k"] == instance["n"] - instance["k"]
    got = solve_clique(instance)
    want = solve_vertex_cover(reduced)
    assert got == want, (label, instance, reduced, got, want)
    return got


# ----------------------------------------------------------------------
# Tests

def test_exhaustive_small():
    count = 0
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, f"n={n} k={k}")
                count += 1
    return count


def test_random_larger():
    rng = random.Random(12345)
    count = 0
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k}, "random")
        count += 1
    return count


def test_edge_cases():
    # k <= 0 always yes for Clique.
    assert solve_clique({"n": 0, "edges": [], "k": 0}) is True
    assert solve_clique({"n": 0, "edges": [], "k": -5}) is True
    # k > n always no for Clique.
    assert solve_clique({"n": 2, "edges": [[0, 1]], "k": 3}) is False
    # Empty graph, no edges: vertex cover empty set works for k >= 0.
    assert solve_vertex_cover({"n": 3, "edges": [], "k": 0}) is True
    # k < 0 always no for Vertex Cover.
    assert solve_vertex_cover({"n": 3, "edges": [[0, 1]], "k": -1}) is False
    # k >= n always yes.
    assert solve_vertex_cover({"n": 3, "edges": [[0, 1]], "k": 3}) is True
    return 6


def main():
    tests_run = 0
    tests_passed = 0
    results = []

    for name, fn in [
        ("test_exhaustive_small", test_exhaustive_small),
        ("test_random_larger", test_random_larger),
        ("test_edge_cases", test_edge_cases),
    ]:
        try:
            c = fn()
            tests_run += c
            tests_passed += c
            results.append(f"PASS {name}: {c} checks")
        except AssertionError as exc:
            tests_run += 1
            results.append(f"FAIL {name}: {exc}")

    for line in results:
        print(line)
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
