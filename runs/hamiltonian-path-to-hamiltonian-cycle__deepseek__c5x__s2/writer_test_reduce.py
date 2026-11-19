"""Brute-force solvers and randomized tests for the Hamiltonian Path ->
Hamiltonian Cycle reduction in reduce.py."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)

def _adj(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def hp_brute(instance):
    """Yes iff some ordering of all vertices is a path in the graph."""
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, edges)
    for perm in itertools.permutations(range(n)):
        if all(perm[i + 1] in adj[perm[i]] for i in range(n - 1)):
            return True
    return False


def hc_brute(instance):
    """Yes iff some cyclic ordering of all vertices is a cycle in the graph."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = _adj(n, edges)
    # Fix the first vertex to 0 to avoid counting rotations/reflections.
    for perm in itertools.permutations(range(1, n)):
        cycle = (0,) + perm
        if all(cycle[(i + 1) % n] in adj[cycle[i]] for i in range(n)):
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def random_graph(rng, n, p):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def all_graphs(n):
    """Every simple graph on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Validate both the source instance and the produced target instance.
        HamiltonianPath.validate(instance)
        reduced = reduce(instance)
        HamiltonianCycle.validate(reduced)
        src = hp_brute(instance)
        tgt = hc_brute(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((instance, reduced, src, tgt))

    # Exhaustive small cases: n = 0, 1, 2, 3, 4.
    for n in range(0, 5):
        for instance in all_graphs(n):
            check(instance)

    # Random larger cases (brute force is factorial, keep n modest).
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 7)
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.8, 1.0])
        check(random_graph(rng, n, p))

    # Explicit edge-case checks.
    assert hp_brute({"n": 0, "edges": []}) is False
    assert hp_brute({"n": 1, "edges": []}) is True
    assert hp_brute({"n": 2, "edges": [[0, 1]]}) is True
    assert hp_brute({"n": 2, "edges": []}) is False
    assert hc_brute({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}) is True
    assert hc_brute({"n": 3, "edges": [[0, 1], [1, 2]]}) is False

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
