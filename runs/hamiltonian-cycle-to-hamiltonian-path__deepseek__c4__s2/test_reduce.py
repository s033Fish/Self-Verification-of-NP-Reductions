"""Brute-force (Held-Karp) solvers and tests for the reduction."""

from __future__ import annotations

import random

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


# ---------------------------------------------------------------- solvers

def _adj(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def has_hamiltonian_cycle(instance) -> bool:
    n = instance["n"]
    if n <= 2:
        return False
    adj = _adj(n, instance["edges"])
    full = (1 << n) - 1
    # dp[mask] = set of endpoints reachable by a path starting at vertex 0
    dp = [0] * (1 << n)
    dp[1] = 1  # path {0} ending at 0
    for mask in range(1 << n):
        ends = dp[mask]
        if not ends:
            continue
        e = ends
        while e:
            v = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[v] & ~mask
            while nxt:
                w = (nxt & -nxt).bit_length() - 1
                nxt &= nxt - 1
                dp[mask | (1 << w)] |= 1 << w
    # any Hamiltonian path from 0 whose last vertex is adjacent to 0
    ends = dp[full]
    while ends:
        v = (ends & -ends).bit_length() - 1
        ends &= ends - 1
        if adj[v] & 1:
            return True
    return False


def has_hamiltonian_path(instance) -> bool:
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, instance["edges"])
    full = (1 << n) - 1
    dp = [0] * (1 << n)
    for v in range(n):
        dp[1 << v] |= 1 << v
    for mask in range(1 << n):
        ends = dp[mask]
        if not ends:
            continue
        e = ends
        while e:
            v = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[v] & ~mask
            while nxt:
                w = (nxt & -nxt).bit_length() - 1
                nxt &= nxt - 1
                dp[mask | (1 << w)] |= 1 << w
    return dp[full] != 0


# ---------------------------------------------------------------- helpers

def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> int:
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianCycle.validate(instance)
        reduced = reduce(instance)
        HamiltonianPath.validate(reduced)
        expected = has_hamiltonian_cycle(instance)
        got = has_hamiltonian_path(reduced)
        assert expected == got, (
            f"mismatch on {instance}: cycle={expected}, reduced={reduced}, path={got}"
        )
        tests_passed += 1

    # exhaustive over all labelled graphs for n = 0..5
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # random graphs on larger n
    rng = random.Random(12345)
    for _ in range(600):
        n = rng.randint(0, 10)
        p = rng.choice([0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
        check(random_graph(n, p, rng))

    # structured cases
    for n in range(3, 12):
        check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})
        check({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]})
        check({"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]})
        check({"n": n, "edges": []})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run


if __name__ == "__main__":
    main()
