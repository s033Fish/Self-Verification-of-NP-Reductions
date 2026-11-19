"""Independent tests for reduce.py: Independent Set -> Clique.

We brute-force both problems from their definitions and compare answers on
many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.


def _adjacency(n, edges):
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    return adj


def solve_independent_set(instance):
    """Yes iff there is an independent set of size >= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = _adjacency(n, edges)
    best = 0
    for size in range(n, 0, -1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if adj[a][b]:
                    ok = False
                    break
            if ok:
                return size >= k
    return False


def solve_clique(instance):
    """Yes iff there is a clique of size >= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = _adjacency(n, edges)
    for size in range(n, 0, -1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if not adj[a][b]:
                    ok = False
                    break
            if ok:
                return size >= k
    return False


# ----------------------------------------------------------------------
# Instance generation helpers.

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield edges


def random_graph(n, rng):
    pairs = list(itertools.combinations(range(n), 2))
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    return edges


# ----------------------------------------------------------------------
# Tests.

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label):
    global tests_run, tests_passed
    tests_run += 1
    IndependentSet.validate(instance)
    out = reduce(instance)
    Clique.validate(out)
    src = solve_independent_set(instance)
    tgt = solve_clique(out)
    if src == tgt:
        tests_passed += 1
    else:
        failures.append((label, instance, out, src, tgt))


def main():
    # Exhaustive: all graphs on n = 0..4, all k in -1..n+1.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-1, n + 2):
                inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
                check(inst, f"exhaustive n={n} edges={edges} k={k}")

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        edges = random_graph(n, rng)
        k = rng.randint(-2, n + 2)
        inst = {"n": n, "edges": edges, "k": k}
        check(inst, f"random n={n} k={k}")

    # Edge cases explicitly.
    check({"n": 0, "edges": [], "k": 0}, "n=0 k=0")
    check({"n": 0, "edges": [], "k": 1}, "n=0 k=1")
    check({"n": 5, "edges": [], "k": 5}, "empty graph k=5")
    check({"n": 5, "edges": [], "k": 6}, "empty graph k=6")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, "triangle k=2")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, "triangle k=1")

    # Orientation / ordering invariance of the reduction.
    inst = {"n": 4, "edges": [[1, 0], [3, 2]], "k": 2}
    check(inst, "reversed orientation")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run, passed, fails = main()
    assert not fails, "some reductions disagreed with brute force"
    print("ALL TESTS PASSED")
