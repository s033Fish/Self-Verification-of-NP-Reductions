"""Independent tests for reduce.py: Vertex Cover -> Clique.

We write our own brute-force solvers from the definitions in problems.py
(which provides no solvers), then compare source answers with the answers of
the reduced target instances over many small instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import VertexCover, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstrings, independent of reduce.py)

def solve_vertex_cover(instance: dict) -> bool:
    """Yes iff there is a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    # Try every subset of size <= k (brute force).
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for (u, v) in edges):
                return True
    return False


def solve_clique(instance: dict) -> bool:
    """Yes iff there is a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def all_graphs(n):
    """All simple undirected graphs on n labelled vertices (edge subsets)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def random_graph(n, rng, p=0.5):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


# ----------------------------------------------------------------------
# Tests

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Validate both instances are well formed.
        try:
            VertexCover.validate(instance)
        except Exception as exc:  # pragma: no cover
            failures.append((label, instance, "invalid source: %r" % (exc,)))
            return
        reduced = reduce(instance)
        try:
            Clique.validate(reduced)
        except Exception as exc:
            failures.append((label, instance, "invalid target: %r" % (exc,)))
            return
        expected = solve_vertex_cover(instance)
        got = solve_clique(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, reduced, expected, got))

    # Exhaustive small graphs, all relevant k values.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": [list(e) for e in edges], "k": k},
                      f"exhaustive n={n} k={k}")

    # Random slightly larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        edges = random_graph(n, rng, p=rng.choice([0.1, 0.3, 0.5, 0.8, 1.0]))
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k}, "random")

    # Targeted edge cases.
    targeted = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 5},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": -5},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 3},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 2},
    ]
    for inst in targeted:
        check(inst, "targeted")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:20]:
            print("FAIL:", f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
