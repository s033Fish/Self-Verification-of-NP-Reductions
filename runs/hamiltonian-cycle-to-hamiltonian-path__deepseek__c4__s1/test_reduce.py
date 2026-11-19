"""Tests for the Hamiltonian Cycle -> Hamiltonian Path reduction.

Independent exact solvers (bitmask DP) for both problems, compared on
many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


def _adj(n, edges):
    a = [[False] * n for _ in range(n)]
    for u, v in edges:
        a[u][v] = True
        a[v][u] = True
    return a


def solve_hp(instance):
    """Exact: True iff the graph has a Hamiltonian path."""
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    a = _adj(n, instance["edges"])
    full = (1 << n) - 1
    # dp[mask][v] = path visiting exactly mask ending at v
    dp = [[False] * n for _ in range(1 << n)]
    for v in range(n):
        dp[1 << v][v] = True
    for mask in range(1 << n):
        row = dp[mask]
        for v in range(n):
            if not row[v]:
                continue
            for w in range(n):
                if not (mask >> w) & 1 and a[v][w]:
                    dp[mask | (1 << w)][w] = True
    return any(dp[full])


def solve_hc(instance):
    """Exact: True iff the graph has a Hamiltonian cycle."""
    n = instance["n"]
    if n <= 2:
        return False
    a = _adj(n, instance["edges"])
    full = (1 << n) - 1
    dp = [[False] * n for _ in range(1 << n)]
    dp[1 << 0][0] = True
    for mask in range(1 << n):
        row = dp[mask]
        for v in range(n):
            if not row[v]:
                continue
            for w in range(n):
                if not (mask >> w) & 1 and a[v][w]:
                    dp[mask | (1 << w)][w] = True
    return any(dp[full][v] and a[v][0] for v in range(n))


def all_graphs(n):
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def check(instance):
    HamiltonianCycle.validate(instance)
    out = reduce(instance)
    HamiltonianPath.validate(out)
    src = solve_hc(instance)
    tgt = solve_hp(out)
    assert src == tgt, (instance, out, src, tgt)
    return src


def main():
    tests_run = 0

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for inst in all_graphs(n):
            check(inst)
            tests_run += 1

    # Random graphs n = 6..9.
    rng = random.Random(12345)
    for n in range(6, 10):
        for _ in range(400):
            p = rng.choice([0.15, 0.3, 0.5, 0.7, 0.9])
            edges = [[u, v] for u, v in itertools.combinations(range(n), 2)
                     if rng.random() < p]
            check({"n": n, "edges": edges})
            tests_run += 1

    # Structured: complete graphs, paths, cycles, stars, near-cycles.
    for n in range(0, 11):
        check({"n": n, "edges": [list(e) for e in itertools.combinations(range(n), 2)]})
        tests_run += 1
        check({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]})
        tests_run += 1
        if n >= 3:
            check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})
            tests_run += 1
            # cycle missing one edge
            check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n - 1)]})
            tests_run += 1
        if n >= 1:
            check({"n": n, "edges": [[0, i] for i in range(1, n)]})
            tests_run += 1

    print(f"tests_run={tests_run} tests_passed={tests_run}")
    return tests_run


if __name__ == "__main__":
    main()
