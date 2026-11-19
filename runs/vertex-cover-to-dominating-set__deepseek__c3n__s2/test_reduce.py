"""Tests comparing brute-force answers on Vertex Cover instances and reductions."""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, DominatingSet
from reduce import reduce


def brute_force_vertex_cover(instance):
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def brute_force_dominating_set(instance):
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if n == 0:
        return k >= 0
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            dominated = set(chosen)
            for v in chosen:
                dominated |= adj[v]
            if len(dominated) == n:
                return True
    return False


def all_graphs(n, max_edges=None):
    pairs = list(itertools.combinations(range(n), 2))
    if max_edges is None:
        max_edges = len(pairs)
    for r in range(0, max_edges + 1):
        for edge_subset in itertools.combinations(pairs, r):
            yield [list(e) for e in edge_subset]


def check(instance):
    VertexCover.validate(instance)
    reduced = reduce(instance)
    DominatingSet.validate(reduced)
    src = brute_force_vertex_cover(instance)
    tgt = brute_force_dominating_set(reduced)
    assert src == tgt, (instance, reduced, src, tgt)
    return src


def main():
    tests_run = 0
    tests_passed = 0

    def run(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Exhaustive small graphs, all k in a wide range (including negatives).
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                run({"n": n, "edges": edges, "k": k})

    # Random medium instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        rng.shuffle(pairs)
        m = rng.randint(0, len(pairs))
        edges = [list(e) for e in pairs[:m]]
        k = rng.randint(-3, n + 2)
        run({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    run({"n": 0, "edges": [], "k": 0})
    run({"n": 0, "edges": [], "k": -1})
    run({"n": 5, "edges": [], "k": 0})          # isolated vertices, no edges
    run({"n": 5, "edges": [], "k": -1})
    run({"n": 3, "edges": [[0, 1]], "k": 0})    # one edge, k=0 -> no
    run({"n": 3, "edges": [[0, 1]], "k": 1})    # yes
    run({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1})  # two components
    run({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})
    run({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]], "k": 2})
    run({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]], "k": 3})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)
    print("verdict.json written")


if __name__ == "__main__":
    main()
