"""Independent tests for reduce.py (Hamiltonian Path -> Hamiltonian Cycle).

We implement our own brute-force solvers from the problem definitions and
compare answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


def _adj(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def has_hamiltonian_path(instance):
    """Brute force: is there a simple path visiting every vertex exactly once?"""
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, edges)
    # DFS over all starting vertices.
    def dfs(v, visited):
        if len(visited) == n:
            return True
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                if dfs(w, visited):
                    return True
                visited.remove(w)
        return False

    for s in range(n):
        if dfs(s, {s}):
            return True
    return False


def has_hamiltonian_cycle(instance):
    """Brute force: is there a cycle visiting every vertex exactly once?"""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = _adj(n, edges)
    # Fix start vertex 0 to avoid rotational duplicates.
    def dfs(v, visited):
        if len(visited) == n:
            return 0 in adj[v]
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                if dfs(w, visited):
                    return True
                visited.remove(w)
        return False

    return dfs(0, {0})


def all_graphs(n):
    """Yield every simple undirected graph on n vertices."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive over all graphs for n = 0..6.
    for n in range(0, 7):
        for inst in all_graphs(n):
            HamiltonianPath.validate(inst)
            expected = has_hamiltonian_path(inst)
            out = reduce(inst)
            HamiltonianCycle.validate(out)
            got = has_hamiltonian_cycle(out)
            tests_run += 1
            if got == expected:
                tests_passed += 1
            else:
                print("MISMATCH", inst, "expected", expected, "got", got, "reduced", out)

    # Random larger graphs.
    import random

    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < rng.choice([0.2, 0.4, 0.6, 0.8])]
        inst = {"n": n, "edges": edges}
        HamiltonianPath.validate(inst)
        expected = has_hamiltonian_path(inst)
        out = reduce(inst)
        HamiltonianCycle.validate(out)
        got = has_hamiltonian_cycle(out)
        tests_run += 1
        if got == expected:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "expected", expected, "got", got, "reduced", out)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
