"""Tests for reduce.py: compare brute-force answers on small instances."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


# ----------------------------------------------------------------------
# Exact solvers (bitmask DP / Held-Karp) written from the definitions.

def _adj_masks(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def solve_hamiltonian_path(instance):
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj_masks(n, instance["edges"])
    full = (1 << n) - 1
    # dp[mask] = set of endpoints v such that a path covering exactly
    # `mask` ends at v.
    dp = [0] * (1 << n)
    for v in range(n):
        dp[1 << v] = 1 << v
    for mask in range(1, 1 << n):
        ends = dp[mask]
        if not ends:
            continue
        if mask == full:
            return True
        e = ends
        while e:
            low = e & -e
            v = low.bit_length() - 1
            e ^= low
            nxt = adj[v] & ~mask
            while nxt:
                b = nxt & -nxt
                w = b.bit_length() - 1
                nxt ^= b
                dp[mask | b] |= b
    return False


def solve_hamiltonian_cycle(instance):
    n = instance["n"]
    if n <= 2:
        return False
    adj = _adj_masks(n, instance["edges"])
    full = (1 << n) - 1
    start = 0
    # dp[mask] = endpoints of paths starting at 0 covering mask.
    dp = [0] * (1 << n)
    dp[1 << start] = 1 << start
    for mask in range(1, 1 << n):
        ends = dp[mask]
        if not ends:
            continue
        e = ends
        while e:
            low = e & -e
            v = low.bit_length() - 1
            e ^= low
            nxt = adj[v] & ~mask
            while nxt:
                b = nxt & -nxt
                w = b.bit_length() - 1
                nxt ^= b
                dp[mask | b] |= b
    ends = dp[full]
    e = ends
    while e:
        low = e & -e
        v = low.bit_length() - 1
        e ^= low
        if adj[v] & (1 << start):
            return True
    return False


# ----------------------------------------------------------------------
# Instance helpers.

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests.

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianCycle.validate(instance)
        reduced = reduce(instance)
        HamiltonianPath.validate(reduced)
        src = solve_hamiltonian_cycle(instance)
        tgt = solve_hamiltonian_path(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((instance, reduced, src, tgt))

    # Exhaustive over all graphs for n = 0..6.
    for n in range(0, 7):
        for g in all_graphs(n):
            check(g)

    # Random graphs for n = 7..10.
    rng = random.Random(12345)
    for n in range(7, 11):
        for _ in range(300):
            p = rng.choice([0.15, 0.3, 0.5, 0.7, 0.9])
            check(random_graph(n, p, rng))

    # A few hand-picked structured cases.
    structured = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},          # triangle: yes
        {"n": 3, "edges": [[0, 1], [1, 2]]},                  # path: no cycle
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},  # C4: yes
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},  # C5
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},          # path: no
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [0, 2]]},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]]},  # path: no
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},  # C4 yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},          # P4 no
    ]
    for g in structured:
        check(g)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for f in failures[:10]:
        print("FAIL", f)

    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    tr, tp, nf = main()
    assert nf == 0, f"{nf} failures"
    print("ALL TESTS PASSED")
