"""Independent verification of reduce.py (Independent Set -> Vertex Cover).

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, generate many small random source instances
(including edge cases), reduce them, and compare answers.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_independent_set(instance: dict) -> bool:
    """Yes iff there is an independent set of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases stated in the docstring.
    if k <= 0:
        return True
    if k > n:
        return False

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Search for any independent set of size >= k.
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(adj[u].isdisjoint(s) for u in s):
                return True
    return False


def solve_vertex_cover(instance: dict) -> bool:
    """Yes iff there is a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases stated in the docstring.
    if k < 0:
        return False
    if k >= n:
        return True

    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            cover = set(subset)
            if all(u in cover or v in cover for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small graphs, all edge cases).

def random_graph(rng: random.Random, n: int, p: float) -> list[list[int]]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def random_instance(rng: random.Random) -> dict:
    n = rng.randint(0, 7)
    p = rng.choice([0.0, 0.2, 0.5, 0.8, 1.0])
    edges = random_graph(rng, n, p)
    # k range deliberately covers k <= 0, 0 <= k <= n, and k > n.
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Both inputs must be valid instances.
        IndependentSet.validate(inst)
        out = reduce(inst)
        VertexCover.validate(out)
        expected = solve_independent_set(inst)
        got = solve_vertex_cover(out)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, inst, out, expected, got))

    # 1. Exhaustive over all graphs on n <= 4 vertices and all k in -2..n+2.
    for n in range(0, 5):
        all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, f"exhaustive n={n} mask={mask} k={k}")

    # 2. Random instances on up to 7 vertices.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng), "random")

    # 3. Explicit edge cases from the docstrings.
    explicit = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 3},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 5, "edges": [], "k": -1},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 0},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": -3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 6},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
    ]
    for inst in explicit:
        check(inst, f"explicit {inst}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for label, inst, out, expected, got in failures[:10]:
            print(f"  {label}: in={inst} out={out} IS={expected} VC={got}")
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
