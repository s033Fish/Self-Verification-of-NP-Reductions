"""Tests for the Hamiltonian Path -> Hamiltonian Cycle reduction."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions

def has_hamiltonian_path(instance):
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for perm in itertools.permutations(range(n)):
        if all(perm[i + 1] in adj[perm[i]] for i in range(n - 1)):
            return True
    return False


def has_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # Fix vertex 0 as the start to avoid counting rotations.
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        cycle = (0,) + perm
        if all(cycle[(i + 1) % n] in adj[cycle[i]] for i in range(n)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    """Yield every simple graph on n vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Both inputs and outputs must be valid instances.
        HamiltonianPath.validate(instance)
        reduced = reduce(instance)
        HamiltonianCycle.validate(reduced)
        expected = has_hamiltonian_path(instance)
        got = has_hamiltonian_cycle(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((instance, reduced, expected, got))

    # Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 8)
        p = rng.choice([0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
        check(random_graph(n, p, rng))

    # Random graphs built to contain a Hamiltonian path (path plus extra edges).
    for _ in range(200):
        n = rng.randint(1, 8)
        perm = list(range(n))
        rng.shuffle(perm)
        edge_set = set()
        for i in range(n - 1):
            a, b = perm[i], perm[i + 1]
            edge_set.add((min(a, b), max(a, b)))
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.3:
                    edge_set.add((u, v))
        g = {"n": n, "edges": [[u, v] for u, v in sorted(edge_set)]}
        check(g)

    # Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": []},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
    ]
    for g in edge_cases:
        check(g)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
