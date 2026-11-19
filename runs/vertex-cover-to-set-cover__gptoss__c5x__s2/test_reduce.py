"""Independent tests for reduce.py (VertexCover -> SetCover).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small source
instances and their reductions.
"""
from __future__ import annotations

import itertools
import random

from problems import VertexCover, SetCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------

def vertex_cover_answer(instance) -> bool:
    """True iff graph has a vertex cover of size <= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # minimum vertex cover by brute force over subsets of vertices
    for size in range(0, n + 1):
        if size > k:
            break
        for combo in itertools.combinations(range(n), size):
            chosen = set(combo)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def set_cover_answer(instance) -> bool:
    """True iff at most k sets cover the whole universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True
    target = set(range(u))
    # if some element is in no set -> no
    available = set()
    for s in sets:
        available.update(s)
    if not target <= available:
        return False
    m = len(sets)
    for size in range(0, min(k, m) + 1):
        for combo in itertools.combinations(range(m), size):
            covered = set()
            for i in combo:
                covered.update(sets[i])
            if covered >= target:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n):
    """All simple graphs on n labelled vertices (as edge lists)."""
    possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for r in range(len(possible) + 1):
        for subset in itertools.combinations(possible, r):
            yield [list(e) for e in subset]


def random_graph(n, p, rng):
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                edges.append([i, j])
    return edges


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        VertexCover.validate(instance)
        expected = vertex_cover_answer(instance)
        target = reduce(instance)
        SetCover.validate(target)
        got = set_cover_answer(target)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((instance, expected, target, got))

    # Exhaustive: all graphs on 0..4 vertices, k from -2..n+2
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Exhaustive on 5 vertices with all k for a sample of graphs
    rng = random.Random(12345)
    for _ in range(300):
        n = 5
        edges = random_graph(n, rng.random(), rng)
        for k in range(-2, n + 3):
            check({"n": n, "edges": edges, "k": k})

    # Random larger instances
    for _ in range(400):
        n = rng.randint(0, 7)
        edges = random_graph(n, rng.random(), rng)
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 3, "edges": [], "k": 0})
    check({"n": 3, "edges": [], "k": -1})
    check({"n": 3, "edges": [[0, 1]], "k": -1})
    check({"n": 3, "edges": [[0, 1]], "k": 0})
    check({"n": 3, "edges": [[0, 1]], "k": 1})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
