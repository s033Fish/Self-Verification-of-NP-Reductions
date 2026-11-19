"""Tests for the Vertex Cover -> Clique reduction.

Includes independent brute-force solvers for both problems, written directly
from the problem definitions, and compares their answers on many small
instances against the answers of the reduction's output.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)
# ----------------------------------------------------------------------

def vertex_cover_brute(instance) -> bool:
    """Yes iff there is a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            cover = set(subset)
            if all(u in cover or v in cover for u, v in edges):
                return True
    return False


def clique_brute(instance) -> bool:
    """Yes iff there is a clique of size AT LEAST k."""
    n = instance["n"]
    edges = instance["edges"]
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
            if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def all_small_instances():
    """Exhaustively enumerate all graphs on n<=4 vertices with k in -1..n+1."""
    for n in range(0, 5):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
            for k in range(-1, n + 2):
                yield {"n": n, "edges": edges, "k": k}


def random_instances(count, seed=12345):
    rng = random.Random(seed)
    for _ in range(count):
        n = rng.randint(0, 8)
        p = rng.choice([0.0, 0.2, 0.5, 0.8, 1.0])
        edges = random_graph(n, p, rng)
        k = rng.randint(-2, n + 2)
        yield {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)
        expected = vertex_cover_brute(instance)
        got = clique_brute(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((instance, reduced, expected, got))

    # 1. Exhaustive small instances.
    for instance in all_small_instances():
        check(instance)

    # 2. Random instances.
    for instance in random_instances(3000):
        check(instance)

    # 3. Explicit edge-case checks.
    edge_cases = [
        {"n": 0, "edges": [], "k": -1},   # no vertices, k<0 -> no
        {"n": 0, "edges": [], "k": 0},    # empty graph -> yes
        {"n": 0, "edges": [], "k": 5},    # k>=n -> yes
        {"n": 5, "edges": [], "k": 0},    # no edges -> yes
        {"n": 5, "edges": [], "k": -1},   # k<0 -> no
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},  # triangle -> yes
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},  # triangle -> no
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},          # two disjoint -> yes
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},          # -> no
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},  # C4 -> yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},  # C4 -> no
        {"n": 6, "edges": [[i, j] for i in range(6) for j in range(i + 1, 6)], "k": 5},
    ]
    for instance in edge_cases:
        check(instance)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
