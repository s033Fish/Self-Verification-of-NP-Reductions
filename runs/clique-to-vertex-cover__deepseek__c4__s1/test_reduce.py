"""Brute-force solvers and tests comparing Clique answers to reduced
Vertex Cover answers on many small instances."""

from __future__ import annotations

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def clique_answer(instance) -> bool:
    """True iff the graph has a clique of at least k vertices."""
    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def vertex_cover_answer(instance) -> bool:
    """True iff the graph has a vertex cover of at most k vertices."""
    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Test helpers.

def random_instance(rng, max_n=6, allow_any_k=True):
    n = rng.randint(0, max_n)
    all_pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(all_pairs)
    m = rng.randint(0, len(all_pairs))
    edges = [list(p) for p in all_pairs[:m]]
    rng.shuffle(edges)
    if allow_any_k:
        k = rng.randint(-2, n + 2)
    else:
        k = rng.randint(0, n)
    return {"n": n, "edges": edges, "k": k}


def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    rng = random.Random(12345)

    # Exhaustive-ish: all graphs on up to 5 vertices, all k in -2..n+2.
    for n in range(0, 6):
        all_pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": edges, "k": k}
                Clique.validate(inst)
                red = reduce(inst)
                VertexCover.validate(red)
                expected = clique_answer(inst)
                got = vertex_cover_answer(red)
                tests_run += 1
                if expected == got:
                    tests_passed += 1
                else:
                    failures.append((inst, red, expected, got))

    # Random larger instances.
    for _ in range(3000):
        inst = random_instance(rng, max_n=8)
        Clique.validate(inst)
        red = reduce(inst)
        VertexCover.validate(red)
        expected = clique_answer(inst)
        got = vertex_cover_answer(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, red, expected, got))

    for inst, red, expected, got in failures[:5]:
        print("FAIL", inst, "->", red, "expected", expected, "got", got)
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed, len(failures) == 0


if __name__ == "__main__":
    run_tests()
