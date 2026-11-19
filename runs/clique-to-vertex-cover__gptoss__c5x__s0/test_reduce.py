"""Independent tests for reduce.py: Clique -> Vertex Cover.

We implement brute-force solvers from the definitions in problems.py, then
compare the answer of every small source instance with the answer of its
reduction.  reduce.py is NOT modified.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the docstrings.

def solve_clique(instance) -> bool:
    """Yes iff the graph has a clique of AT LEAST k vertices."""
    Clique.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the definition.
    if k <= 0:
        return True
    if k > n:
        return False
    if k == 1:
        return n >= 1

    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    # Try every subset of size >= k (only sizes k..n matter).
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


def solve_vertex_cover(instance) -> bool:
    """Yes iff the graph has a vertex cover of AT MOST k vertices."""
    VertexCover.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the definition.
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers a graph with no edges
    if k >= n:
        return True  # all vertices cover every edge

    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def all_graphs(n):
    """All simple undirected graphs on n labelled vertices (edge lists)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def random_instance(rng, max_n=6):
    n = rng.randint(0, max_n)
    pairs = list(itertools.combinations(range(n), 2))
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Test driver.

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            src_ans = solve_clique(inst)
            red = reduce(inst)
            # The reduction must return a valid target instance.
            VertexCover.validate(red)
            tgt_ans = solve_vertex_cover(red)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, inst, f"exception: {exc!r}"))
            return
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append((label, inst, red, src_ans, tgt_ans))

    # 1. Exhaustive: every graph on 0..4 vertices, every k in a wide range.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k},
                      f"exhaustive n={n} k={k} edges={edges}")

    # 2. Exhaustive on n=5 (1024 graphs) with a few k values.
    for edges in all_graphs(5):
        for k in range(-1, 7):
            check({"n": 5, "edges": edges, "k": k}, "exhaustive n=5")

    # 3. Random instances, larger n.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng, max_n=7), "random")

    # 4. Targeted edge cases.
    targeted = [
        {"n": 0, "edges": [], "k": 0},     # yes (k<=0)
        {"n": 0, "edges": [], "k": 1},     # no (k>n)
        {"n": 0, "edges": [], "k": -5},    # yes (k<=0)
        {"n": 1, "edges": [], "k": 1},     # yes (k=1, n>=1)
        {"n": 1, "edges": [], "k": 2},     # no
        {"n": 3, "edges": [], "k": 1},     # yes (k=1)
        {"n": 3, "edges": [], "k": 2},     # no (no edges -> max clique 1)
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},  # yes
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4},  # no
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},          # yes
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 3},          # no
        {"n": 5, "edges": [[0, 1]], "k": -1},                 # yes
        {"n": 5, "edges": [[0, 1]], "k": 0},                  # yes
    ]
    for inst in targeted:
        check(inst, "targeted")

    # 5. Confirm the reduction is not calling a brute-force solver and that
    #    it is deterministic / polynomial-shaped: just call it a lot.
    for _ in range(200):
        check(random_instance(rng, max_n=8), "random-big")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
