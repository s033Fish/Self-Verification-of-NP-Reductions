"""Brute-force solvers and tests comparing HP answers with reduced HC answers."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the definitions.

def _adj(n, edges):
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def solve_hamiltonian_path(instance):
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


def solve_hamiltonian_cycle(instance):
    """Yes iff some cyclic ordering of all vertices uses only graph edges."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = _adj(n, edges)
    # Fix vertex 0 as the start to avoid counting rotations; also fix the
    # direction by requiring perm[1] < perm[-1].
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        cycle = (0,) + perm
        if all(cycle[(i + 1) % n] in adj[cycle[i]] for i in range(n)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation: all graphs on small n, plus random graphs.

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < 0.5:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianPath.validate(instance)
        reduced = reduce(instance)
        HamiltonianCycle.validate(reduced)
        expected = solve_hamiltonian_path(instance)
        got = solve_hamiltonian_cycle(reduced)
        assert expected == got, (instance, reduced, expected, got)
        tests_passed += 1

    # Exhaustive over all graphs for n = 0..6.
    for n in range(0, 7):
        for inst in all_graphs(n):
            check(inst)

    # Random graphs on larger n (still brute-forceable).
    rng = random.Random(12345)
    for n in range(7, 10):
        for _ in range(200):
            check(random_graph(n, rng))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
