"""Tests for the Vertex Cover -> Dominating Set reduction."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions in problems.py

def vertex_cover_yes(instance: dict) -> bool:
    """Yes iff graph has a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for comb in itertools.combinations(range(n), size):
            chosen = set(comb)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def dominating_set_yes(instance: dict) -> bool:
    """Yes iff graph has a dominating set of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for comb in itertools.combinations(range(n), size):
            chosen = set(comb)
            dominated = set(chosen)
            for x in chosen:
                dominated |= adj[x]
            if len(dominated) == n:
                return True
    return False


def all_graphs(n: int):
    """Yield every simple undirected graph on n labelled vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield edges


def random_graph(rng: random.Random, n: int) -> list[list[int]]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < 0.4:
                edges.append([u, v])
    return edges


def check(instance: dict) -> bool:
    """Validate, reduce, validate the reduction, compare answers."""
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    src = vertex_cover_yes(instance)
    tgt = dominating_set_yes(reduced)
    assert src == tgt, (instance, reduced, src, tgt)
    return src


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # Exhaustive: all graphs on n = 0..4 vertices, all k in -2..n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                run({"n": n, "edges": edges, "k": k})

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        edges = random_graph(rng, n)
        k = rng.randint(-2, n + 2)
        run({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    run({"n": 0, "edges": [], "k": 0})
    run({"n": 0, "edges": [], "k": -1})
    run({"n": 5, "edges": [], "k": 0})          # no edges, k >= 0 -> yes
    run({"n": 5, "edges": [], "k": -1})         # k < 0 -> no
    run({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1})  # path, min VC = 1
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1})
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2})
    # isolated vertices force the +m offset
    run({"n": 4, "edges": [[0, 1]], "k": 0})    # needs 1 cover + 2 isolated
    run({"n": 4, "edges": [[0, 1]], "k": 1})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})  # triangle

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)


if __name__ == "__main__":
    main()
