"""Brute-force solvers and tests for the Vertex Cover -> Dominating Set reduction."""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from problems import VertexCover, DominatingSet


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def vertex_cover_yes(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def dominating_set_yes(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            dominated = set(chosen)
            for v in chosen:
                dominated |= adj[v]
            if len(dominated) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators.

def all_graphs(n):
    """Yield every simple undirected graph on n vertices as an edge list."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        yield [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


# ----------------------------------------------------------------------
# Tests.

def check(instance):
    VertexCover.validate(instance)
    out = reduce(instance)
    DominatingSet.validate(out)
    expected = vertex_cover_yes(instance)
    got = dominating_set_yes(out)
    assert expected == got, (
        f"mismatch for {instance}: VC={expected}, DS(reduced)={got}, reduced={out}"
    )


def main():
    tests_run = 0

    # Exhaustive: all graphs on 0..5 vertices, all relevant k.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})
                tests_run += 1

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(800):
        n = rng.randint(0, 7)
        edges = random_graph(n, rng.random(), rng)
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})
        tests_run += 1

    # Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 6, "edges": [[0, 1], [2, 3]], "k": 0},  # isolated vertices present
    ]
    for instance in edge_cases:
        check(instance)
        tests_run += 1

    print(f"tests_run={tests_run} tests_passed={tests_run}")
    return tests_run


if __name__ == "__main__":
    main()
