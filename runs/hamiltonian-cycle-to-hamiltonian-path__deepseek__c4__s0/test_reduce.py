"""Brute-force solvers and tests for the Hamiltonian Cycle -> Path reduction."""

from __future__ import annotations

import random

from reduce import reduce


def _adj(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def solve_hamiltonian_path(instance):
    """Backtracking brute force: is there a Hamiltonian path?"""
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, instance["edges"])

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

    for start in range(n):
        if dfs(start, {start}):
            return True
    return False


def solve_hamiltonian_cycle(instance):
    """Backtracking brute force: is there a Hamiltonian cycle?"""
    n = instance["n"]
    if n <= 2:
        return False
    adj = _adj(n, instance["edges"])

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
    """Yield every simple graph on n labelled vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def validate_target(red):
    assert set(red) == {"n", "edges"}, red
    assert isinstance(red["n"], int) and not isinstance(red["n"], bool)
    assert red["n"] >= 0
    assert isinstance(red["edges"], list)
    seen = set()
    for e in red["edges"]:
        assert isinstance(e, list) and len(e) == 2, e
        u, v = e
        assert isinstance(u, int) and not isinstance(u, bool)
        assert isinstance(v, int) and not isinstance(v, bool)
        assert 0 <= u < red["n"] and 0 <= v < red["n"], e
        assert u != v, e
        key = frozenset((u, v))
        assert key not in seen, f"duplicate edge {e}"
        seen.add(key)


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src = solve_hamiltonian_cycle(inst)
        red = reduce(inst)
        validate_target(red)
        tgt = solve_hamiltonian_path(red)
        if src != tgt:
            failures.append((inst, red, src, tgt))
        else:
            tests_passed += 1

    # Exhaustive over all graphs for n = 0..5.
    for n in range(0, 6):
        for inst in all_graphs(n):
            check(inst)

    # Random larger graphs.
    rng = random.Random(12345)
    for n in range(6, 9):
        for _ in range(300):
            p = rng.choice([0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
            check(random_graph(n, p, rng))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print("  ", f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
