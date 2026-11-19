"""Tests for the Clique -> Vertex Cover reduction.

Includes brute-force solvers for both problems written from the definitions
in problems.py, and compares answers on many small random instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce


# ---------------------------------------------------------------- solvers


def clique_solver(instance: dict) -> bool:
    """Brute force: is there a clique of size >= k?"""
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

    # Find the maximum clique size by checking subsets (n is small in tests).
    for size in range(n, 0, -1):
        if size < k:
            return False
        for subset in itertools.combinations(range(n), size):
            if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
                return True
    return k <= 0


def vertex_cover_solver(instance: dict) -> bool:
    """Brute force: is there a vertex cover of size <= k?"""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True

    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


# ---------------------------------------------------------------- helpers


def random_graph(n: int, p: float, rng: random.Random) -> list[list[int]]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def make_instance(n, edges, k):
    return {"n": n, "edges": edges, "k": k}


def run_tests() -> tuple[int, int]:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        Clique.validate(instance)
        reduced = reduce(instance)
        VertexCover.validate(reduced)
        expected = clique_solver(instance)
        got = vertex_cover_solver(reduced)
        assert got == expected, (
            f"mismatch on {instance}: clique={expected}, "
            f"reduced={reduced}, cover={got}"
        )
        tests_passed += 1

    # Exhaustive small graphs: n in 0..4, all edge subsets, all k in -2..n+2.
    for n in range(0, 5):
        pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                check(make_instance(n, edges, k))

    # Random graphs, larger n.
    for _ in range(400):
        n = rng.randint(0, 8)
        p = rng.choice([0.0, 0.2, 0.5, 0.8, 1.0])
        edges = random_graph(n, p, rng)
        k = rng.randint(-3, n + 3)
        check(make_instance(n, edges, k))

    # Explicit edge cases.
    check(make_instance(0, [], 0))     # empty graph, k=0 -> yes
    check(make_instance(0, [], 1))     # empty graph, k=1 -> no
    check(make_instance(3, [], 0))     # no edges, k=0 -> yes
    check(make_instance(3, [], 2))     # no edges, k=2 -> no
    check(make_instance(3, [[0, 1], [1, 2], [0, 2]], 3))  # triangle, k=3 -> yes
    check(make_instance(3, [[0, 1], [1, 2], [0, 2]], 4))  # k>n -> no
    check(make_instance(3, [[0, 1], [1, 2], [0, 2]], -5))  # k<=0 -> yes
    check(make_instance(1, [], 1))     # single vertex, k=1 -> yes
    check(make_instance(1, [], 2))     # single vertex, k=2 -> no

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed, "some tests failed"
    print("ALL TESTS PASSED")
