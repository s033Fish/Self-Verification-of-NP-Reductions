"""Brute-force solvers and tests for the Clique -> Vertex Cover reduction."""

from __future__ import annotations

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written directly from the docstring definitions).

def has_clique(n, edges, k):
    """Yes iff graph has a clique of at least k vertices."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for size in range(k, n + 1):
        for verts in itertools.combinations(range(n), size):
            if all(adj[u][v] for u, v in itertools.combinations(verts, 2)):
                return True
    return False


def has_vertex_cover(n, edges, k):
    """Yes iff graph has a vertex cover of at most k vertices."""
    if k < 0:
        return False
    if not edges:
        return True
    for size in range(0, min(k, n) + 1):
        for verts in itertools.combinations(range(n), size):
            covered = set(verts)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


def clique_answer(inst):
    return has_clique(inst["n"], inst["edges"], inst["k"])


def vertex_cover_answer(inst):
    return has_vertex_cover(inst["n"], inst["edges"], inst["k"])


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0


def check(inst, label=""):
    global tests_run, tests_passed
    tests_run += 1
    Clique.validate(inst)
    out = reduce(inst)
    VertexCover.validate(out)
    src = clique_answer(inst)
    tgt = vertex_cover_answer(out)
    if src == tgt:
        tests_passed += 1
    else:
        print(f"FAIL {label}: {inst} -> {out}  src={src} tgt={tgt}")


def all_graphs(n):
    """All simple graphs on n vertices, as edge lists."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if mask >> i & 1]


def main():
    # 1. Exhaustive: all graphs on 0..4 vertices, all k in -2..n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k},
                      f"exhaustive n={n}")

    # 2. Random small instances, including reversed edge orientation.
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        edges = []
        for u, v in pairs:
            if rng.random() < 0.5:
                edges.append([v, u] if rng.random() < 0.5 else [u, v])
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k}, "random")

    # 3. Targeted edge cases.
    targeted = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 1},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [], "k": 4},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 3},
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 2},
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 3},
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3]], "k": 3},
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3]], "k": 4},
    ]
    for inst in targeted:
        check(inst, "targeted")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
