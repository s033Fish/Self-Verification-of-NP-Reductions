"""Tests comparing brute-force solvers on small Vertex Cover instances and
their reductions to Clique."""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def vertex_cover_yes(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True

    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def clique_yes(instance: dict) -> bool:
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

    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if not adj[a][b]:
                    ok = False
                    break
            if ok:
                return True
    return False


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0


def check(instance: dict, label: str = "") -> None:
    global tests_run, tests_passed
    tests_run += 1

    VertexCover.validate(instance)
    reduced = reduce(instance)
    Clique.validate(reduced)

    expected = vertex_cover_yes(instance)
    got = clique_yes(reduced)

    if expected == got:
        tests_passed += 1
    else:
        raise AssertionError(
            f"mismatch {label}: instance={instance} reduced={reduced} "
            f"source_yes={expected} target_yes={got}"
        )


def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def main() -> None:
    # Exhaustive over all graphs with n <= 4 and all relevant k values.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, f"exhaustive n={n}")

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0}, "n=0 k=0")
    check({"n": 0, "edges": [], "k": -1}, "n=0 k=-1")
    check({"n": 5, "edges": [], "k": 0}, "no edges k=0")
    check({"n": 5, "edges": [], "k": -1}, "no edges k=-1")
    check({"n": 5, "edges": [], "k": 5}, "no edges k=n")
    check({"n": 5, "edges": [], "k": 10}, "no edges k>n")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, "triangle k=2")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, "triangle k=1")
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, "matching k=2")
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}, "matching k=1")

    # Random small instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 7)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.4]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k}, "random")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
