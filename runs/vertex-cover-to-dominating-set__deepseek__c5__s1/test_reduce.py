"""Independent tests for reduce.py (Vertex Cover -> Dominating Set).

We write brute-force solvers for both problems straight from the docstrings,
then compare the source answer with the target answer on the reduction, over
exhaustive small graphs and random slightly larger graphs.
"""
from __future__ import annotations

import itertools
import random

from problems import VertexCover, DominatingSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)

def _adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def vc_solve(instance) -> bool:
    """Vertex Cover: exists a set of <= k vertices covering every edge."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
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


def ds_solve(instance) -> bool:
    """Dominating Set: exists a set of <= k vertices dominating all vertices."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    adj = _adjacency(n, edges)
    for size in range(0, k + 1):
        for comb in itertools.combinations(range(n), size):
            chosen = set(comb)
            if all(v in chosen or (adj[v] & chosen) for v in range(n)):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def all_graphs(n):
    """All simple undirected graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src = vc_solve(inst)
        red = reduce(inst)
        # the reduction must produce a valid target instance
        try:
            DominatingSet.validate(red)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, inst, red, "invalid target instance: %r" % exc))
            return
        tgt = ds_solve(red)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((label, inst, red, "src=%s tgt=%s" % (src, tgt)))

    # Exhaustive: all graphs on n = 0..5, all relevant k.
    for n in range(0, 6):
        for g in all_graphs(n):
            for k in range(-1, n + 2):
                inst = {"n": g["n"], "edges": g["edges"], "k": k}
                check(inst, "exhaustive n=%d" % n)

    # Random: n = 6,7 with several densities and k values.
    rng = random.Random(12345)
    for n in (6, 7):
        for p in (0.0, 0.15, 0.3, 0.5, 0.8, 1.0):
            for _ in range(40):
                g = random_graph(n, p, rng)
                for k in range(-1, n + 2):
                    inst = {"n": g["n"], "edges": g["edges"], "k": k}
                    check(inst, "random n=%d" % n)

    print("tests_run=%d tests_passed=%d" % (tests_run, tests_passed))
    if failures:
        print("FAILURES: %d" % len(failures))
        for f in failures[:10]:
            print(f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
