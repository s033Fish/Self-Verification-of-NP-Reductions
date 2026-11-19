"""Tests for the Clique -> Vertex Cover reduction.

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)
# ----------------------------------------------------------------------

def clique_bruteforce(instance: dict) -> bool:
    """Yes iff G has a clique of size >= k."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    # Try every subset of size k (clique of size >= k exists iff size k does).
    for subset in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
            return True
    return False


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Yes iff G has a vertex cover of size <= k."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
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


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_graph(n: int, p: float, rng: random.Random) -> list[list[int]]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def all_small_instances():
    """Exhaustive-ish enumeration over tiny graphs and a range of k."""
    rng = random.Random(12345)
    instances = []
    # All graphs on n <= 4 vertices (2^(n choose 2) of them).
    for n in range(0, 5):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                instances.append({"n": n, "edges": edges, "k": k})
    # Random graphs on up to 7 vertices.
    for _ in range(400):
        n = rng.randint(0, 7)
        edges = random_graph(n, rng.random(), rng)
        k = rng.randint(-2, n + 2)
        instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    instances = all_small_instances()
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in instances:
        Clique.validate(inst)  # source instance must be valid
        reduced = reduce(inst)
        VertexCover.validate(reduced)  # target instance must be valid

        source_answer = clique_bruteforce(inst)
        target_answer = vertex_cover_bruteforce(reduced)
        tests_run += 1
        if source_answer == target_answer:
            tests_passed += 1
        else:
            failures.append((inst, reduced, source_answer, target_answer))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for f in failures[:10]:
            print("FAIL:", f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
