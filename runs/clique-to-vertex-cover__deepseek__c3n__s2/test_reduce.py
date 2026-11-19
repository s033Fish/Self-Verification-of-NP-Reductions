"""Tests for the Clique -> Vertex Cover reduction in reduce.py.

Brute-force solvers are written directly from the problem definitions in
problems.py (which provides no solvers).  We then compare the solvers'
answers on many small Clique instances with the answers on their reductions.
"""

from __future__ import annotations

import json
from itertools import combinations

from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)

def brute_clique(instance: dict) -> bool:
    """Yes iff the graph has a clique of AT LEAST k vertices."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for size in range(k, n + 1):
        for comb in combinations(range(n), size):
            if all(adj[a][b] for a, b in combinations(comb, 2)):
                return True
    return False


def brute_vertex_cover(instance: dict) -> bool:
    """Yes iff the graph has a vertex cover of AT MOST k vertices."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for comb in combinations(range(n), size):
            chosen = set(comb)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation: every graph on n vertices, several k values.

def all_graphs(n: int):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def k_values(n: int):
    return range(-2, n + 3)


def run_tests() -> tuple[int, int]:
    tests_run = 0
    tests_passed = 0
    failures = []

    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in k_values(n):
                instance = {"n": n, "edges": edges, "k": k}
                Clique.validate(instance)

                reduced = reduce(instance)
                VertexCover.validate(reduced)

                expected = brute_clique(instance)
                got = brute_vertex_cover(reduced)

                tests_run += 1
                if expected == got:
                    tests_passed += 1
                else:
                    failures.append((instance, reduced, expected, got))

    # A few larger random-ish structured instances for extra confidence.
    import random

    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 8)
        pairs = list(combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-2, n + 2)
        instance = {"n": n, "edges": edges, "k": k}
        Clique.validate(instance)

        reduced = reduce(instance)
        VertexCover.validate(reduced)

        expected = brute_clique(instance)
        got = brute_vertex_cover(reduced)

        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((instance, reduced, expected, got))

    for instance, reduced, expected, got in failures[:10]:
        print("FAIL:", instance, "->", reduced, "expected", expected, "got", got)
    return tests_run, tests_passed


if __name__ == "__main__":
    tests_run, tests_passed = run_tests()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    verified = tests_run > 0 and tests_run == tests_passed
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )
    print("verdict:", {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed})
