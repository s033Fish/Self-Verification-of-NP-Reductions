"""Independent verification of reduce.py (Clique -> Vertex Cover).

We implement brute-force solvers directly from the docstrings in problems.py,
then exhaustively compare SOURCE answers with the answers of the reduced
TARGET instances on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)
# ----------------------------------------------------------------------

def solve_clique(instance) -> bool:
    """Yes iff G has a clique of AT LEAST k vertices."""
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

    # A clique of size >= k exists iff some k-subset is a clique.
    for subset in itertools.combinations(range(n), k):
        ok = True
        for a, b in itertools.combinations(subset, 2):
            if not adj[a][b]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_vertex_cover(instance) -> bool:
    """Yes iff G has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True  # all vertices cover every edge (also handles n == 0)

    # Try every subset of vertices of size <= k.
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def all_graphs(n):
    """Yield every simple undirected graph on n vertices as an edge list."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]


def random_graph(n, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < 0.5:
            edges.append([u, v])
    return edges


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src = solve_clique(instance)
        target = reduce(instance)
        # The produced target must itself be a valid VertexCover instance.
        VertexCover.validate(target)
        tgt = solve_vertex_cover(target)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((label, instance, target, src, tgt))

    # Exhaustive: all graphs on n = 0..5 vertices, all k in -2..n+2.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
                Clique.validate(inst)
                check(inst, f"exhaustive n={n} k={k} edges={edges}")

    # Randomised larger instances (n up to 8), k in -3..n+3.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        edges = random_graph(n, rng)
        k = rng.randint(-3, n + 3)
        inst = {"n": n, "edges": edges, "k": k}
        Clique.validate(inst)
        check(inst, f"random n={n} k={k} edges={edges}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, inst, target, src, tgt in failures[:10]:
            print("  ", label, "->", target, "src=", src, "tgt=", tgt)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()
