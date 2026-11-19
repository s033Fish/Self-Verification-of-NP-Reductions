"""Brute-force (bitmask DP) solvers and tests for the HC -> HP reduction."""

from __future__ import annotations

import random

import problems
from reduce import reduce


def _adj(n, edges):
    a = [0] * n
    for u, v in edges:
        a[u] |= 1 << v
        a[v] |= 1 << u
    return a


def solve_hc(instance):
    """Exact Hamiltonian Cycle via bitmask DP."""
    n = instance["n"]
    if n <= 2:
        return False
    adj = _adj(n, instance["edges"])
    full = (1 << n) - 1
    # dp[mask] = bitmask of possible endpoints of a path starting at 0.
    dp = [0] * (1 << n)
    dp[1] = 1  # path {0} ending at 0
    for mask in range(1 << n):
        ends = dp[mask]
        if not ends:
            continue
        for v in range(n):
            if ends >> v & 1:
                nxt = adj[v] & ~mask
                while nxt:
                    b = nxt & -nxt
                    w = b.bit_length() - 1
                    dp[mask | b] |= b
                    nxt ^= b
    ends = dp[full]
    return any((ends >> v & 1) and (adj[v] >> 0 & 1) for v in range(n))


def solve_hp(instance):
    """Exact Hamiltonian Path via bitmask DP."""
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
        for v in range(n):
            if ends >> v & 1:
                nxt = adj[v] & ~mask
                while nxt:
                    b = nxt & -nxt
                    dp[mask | b] |= b
                    nxt ^= b
    return dp[full] != 0


def all_graphs(n):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive over ALL graphs for n = 0..6.
    for n in range(0, 7):
        for inst in all_graphs(n):
            tests_run += 1
            problems.HamiltonianCycle.validate(inst)
            out = reduce(inst)
            problems.HamiltonianPath.validate(out)
            expected = solve_hc(inst)
            got = solve_hp(out)
            if expected != got:
                print("FAIL", inst, "->", out, "expected", expected, "got", got)
            else:
                tests_passed += 1

    # Random graphs up to n = 11.
    rng = random.Random(12345)
    for _ in range(6000):
        n = rng.randint(0, 11)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        p = rng.choice([0.15, 0.3, 0.5, 0.8])
        edges = [list(e) for e in possible if rng.random() < p]
        inst = {"n": n, "edges": edges}
        tests_run += 1
        problems.HamiltonianCycle.validate(inst)
        out = reduce(inst)
        problems.HamiltonianPath.validate(out)
        expected = solve_hc(inst)
        got = solve_hp(out)
        if expected != got:
            print("FAIL", inst, "->", out, "expected", expected, "got", got)
        else:
            tests_passed += 1

    # Known cases.
    known = [
        ({"n": 0, "edges": []}, False),
        ({"n": 1, "edges": []}, False),
        ({"n": 2, "edges": [[0, 1]]}, False),
        ({"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2]]}, False),
        ({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]}, True),
        ({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]}, False),
        ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}, True),
        ({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]}, True),
        # K4 minus edge {2,3}: still has HC 0-2-1-3-0.
        ({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]]}, True),
        # Star K1,3: has HP but no HC.
        ({"n": 4, "edges": [[0, 1], [0, 2], [0, 3]]}, False),
    ]
    for inst, expected in known:
        tests_run += 1
        out = reduce(inst)
        got = solve_hp(out)
        if expected != got:
            print("FAIL known", inst, "->", out, "expected", expected, "got", got)
        else:
            tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
