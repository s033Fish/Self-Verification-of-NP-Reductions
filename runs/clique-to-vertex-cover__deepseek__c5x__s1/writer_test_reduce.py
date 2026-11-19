"""Tests for the Clique -> Vertex Cover reduction.

Contains brute-force solvers for both problems (written from the problem
docstrings, since problems.py provides none) and compares the answers on many
small source instances against their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)

def clique_answer(instance: dict) -> bool:
    """True iff the graph has a clique of at least k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def vertex_cover_answer(instance: dict) -> bool:
    """True iff the graph has a vertex cover of at most k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k < 0:
        return False
    edges = instance["edges"]
    if not edges:
        return True  # empty set covers a graph with no edges
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n: int):
    """Yield every simple undirected graph on n vertices as an edge list."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        yield [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]


def check(instance: dict) -> bool:
    """Validate, solve source, reduce, validate, solve target; compare."""
    Clique.validate(instance)
    source_yes = clique_answer(instance)
    reduced = reduce(instance)
    VertexCover.validate(reduced)
    target_yes = vertex_cover_answer(reduced)
    assert source_yes == target_yes, (
        f"mismatch: source={instance} -> {source_yes}, "
        f"reduced={reduced} -> {target_yes}"
    )
    return True


# ----------------------------------------------------------------------
# Tests

def test_exhaustive_small():
    """Exhaustively test all graphs up to n=4 and a range of k values."""
    tests = 0
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})
                tests += 1
    return tests


def test_random_medium():
    """Randomized tests on slightly larger graphs."""
    rng = random.Random(12345)
    tests = 0
    for _ in range(400):
        n = rng.randint(0, 8)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < 0.4]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})
        tests += 1
    return tests


def test_edge_cases():
    tests = 0
    cases = [
        # k <= 0 always yes for clique; target k' >= n always yes.
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -5},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        # k = 1 yes whenever n >= 1.
        {"n": 1, "edges": [], "k": 1},
        {"n": 5, "edges": [], "k": 1},
        # k > n always no.
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4},
        {"n": 0, "edges": [], "k": 1},
        # Complete graphs: clique yes at k = n, target k' = 0 with no edges.
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 4},
        # Empty graph: clique only for k <= 1, complement is complete.
        {"n": 4, "edges": [], "k": 2},
        # Triangle plus isolated vertex.
        {"n": 4, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
        {"n": 4, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
    ]
    for instance in cases:
        check(instance)
        tests += 1
    return tests


def test_reduction_shape():
    """The reduction must keep n and produce the complement edge set."""
    instance = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
    reduced = reduce(instance)
    assert reduced["n"] == 4
    assert reduced["k"] == 4 - 2
    expected = [[0, 2], [0, 3], [1, 2], [1, 3]]
    assert sorted(map(tuple, reduced["edges"])) == sorted(map(tuple, expected))
    VertexCover.validate(reduced)
    return 1


def main():
    total = 0
    passed = 0
    for test in (
        test_exhaustive_small,
        test_random_medium,
        test_edge_cases,
        test_reduction_shape,
    ):
        count = test()
        total += count
        passed += count
        print(f"{test.__name__}: {count} checks passed")
    print(f"TOTAL: {passed}/{total} checks passed")
    return passed, total


if __name__ == "__main__":
    main()
