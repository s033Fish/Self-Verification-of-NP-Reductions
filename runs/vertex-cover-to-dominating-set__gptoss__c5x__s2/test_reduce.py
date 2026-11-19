"""Independent brute-force check of reduce.py (Vertex Cover -> Dominating Set).

Solvers are written directly from the problem definitions in problems.py.
We exhaustively compare source answers with the answers of their reductions
on all small graphs plus random and hand-picked edge cases.
"""
from __future__ import annotations

import itertools
import random

from problems import VertexCover, DominatingSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def vertex_cover_yes(instance) -> bool:
    """Yes iff graph has a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
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


def dominating_set_yes(instance) -> bool:
    """Yes iff graph has a dominating set of size AT MOST k.

    Branch and bound: pick the lowest undominated vertex v; any dominating
    set must contain v or one of v's neighbours.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True

    closed = [1 << v for v in range(n)]
    for u, v in edges:
        closed[u] |= 1 << v
        closed[v] |= 1 << u
    full = (1 << n) - 1
    memo = {}

    def rec(dom, budget):
        if dom == full:
            return True
        if budget == 0:
            return False
        key = (dom, budget)
        if key in memo:
            return memo[key]
        # lowest undominated vertex
        undom = (~dom) & full
        v = (undom & -undom).bit_length() - 1
        # candidates: v itself and its neighbours
        cand = closed[v]
        c = cand
        while c:
            bit = c & -c
            c ^= bit
            if rec(dom | closed[bit.bit_length() - 1], budget - 1):
                memo[key] = True
                return True
        memo[key] = False
        return False

    return rec(0, k)


# ----------------------------------------------------------------------
# Instance generators.

def all_graphs(n):
    """Yield every simple undirected graph on n vertices as edge lists."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if (mask >> i) & 1]
        yield edges


def random_graph(n, rng, p=0.5):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        VertexCover.validate(instance)
        src = vertex_cover_yes(instance)
        reduced = reduce(instance)
        DominatingSet.validate(reduced)
        tgt = dominating_set_yes(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((instance, reduced, src, tgt))

    # Exhaustive: all graphs on 0..4 vertices, k from -2 to n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random graphs on 5..8 vertices.
    rng = random.Random(12345)
    for n in range(5, 9):
        for _ in range(120):
            edges = random_graph(n, rng, p=rng.choice([0.15, 0.3, 0.5, 0.8]))
            for k in range(-1, n + 2):
                check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 2},
        {"n": 2, "edges": [[0, 1]], "k": 0},
        {"n": 2, "edges": [[0, 1]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]], "k": 1},
        {"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]], "k": 0},
        {"n": 7, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2},
        {"n": 7, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3},
    ]
    for instance in edge_cases:
        check(instance)


    # Extra randomized tests on larger graphs (k kept small for brute force).
    rng2 = random.Random(999)
    for _ in range(3000):
        n = rng2.randint(5, 11)
        p = rng2.choice([0.1, 0.25, 0.5, 0.75, 1.0])
        edges = random_graph(n, rng2, p)
        k = rng2.randint(-1, min(n, 4))
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for inst, red, src, tgt in failures[:10]:
            print("  instance:", inst)
            print("  reduced :", red)
            print("  src_yes :", src, " tgt_yes:", tgt)
    else:
        print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
