"""Tests for the Vertex Cover -> Clique reduction."""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, Clique
from reduce import reduce


def solve_vertex_cover(instance):
    """Brute force: is there a vertex cover of size <= k?"""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_clique(instance):
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
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def run_tests():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        VertexCover.validate(instance)
        reduced = reduce(instance)
        Clique.validate(reduced)
        expected = solve_vertex_cover(instance)
        got = solve_clique(reduced)
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", instance, "->", reduced, "expected", expected, "got", got)
        return expected == got

    # Exhaustive over all graphs on n <= 4 and all k in a range.
    for n in range(0, 5):
        all_pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(2000):
        n = rng.randint(0, 9)
        p = rng.random()
        edges = random_graph(n, p, rng)
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    return tests_run, tests_passed


if __name__ == "__main__":
    total, passed = run_tests()
    print(f"tests_run={total} tests_passed={passed}")
    assert total == passed, "some tests failed"
