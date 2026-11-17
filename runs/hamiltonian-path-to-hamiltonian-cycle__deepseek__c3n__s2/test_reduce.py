"""Tests for the Hamiltonian Path -> Hamiltonian Cycle reduction."""

from __future__ import annotations

import itertools
from typing import Any

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def _adj(n: int, edges: list[list[int]]) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def solve_path(instance: dict[str, Any]) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, edges)
    # DP over subsets: reachable[mask][v] = a path covering mask ending at v.
    reachable = [0] * (1 << n)
    for v in range(n):
        reachable[1 << v] |= (1 << v)
    for mask in range(1 << n):
        bits = reachable[mask]
        while bits:
            low = bits & -bits
            v = low.bit_length() - 1
            bits ^= low
            for w in adj[v]:
                if not (mask >> w) & 1:
                    reachable[mask | (1 << w)] |= (1 << w)
    return reachable[(1 << n) - 1] != 0


def solve_cycle(instance: dict[str, Any]) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = _adj(n, edges)
    # Fix vertex 0 as the start; DP over subsets containing 0.
    full = (1 << n) - 1
    reachable = [0] * (1 << n)
    reachable[1] |= 1  # path {0} ending at 0
    for mask in range(1 << n):
        if not (mask & 1):
            continue
        bits = reachable[mask]
        while bits:
            low = bits & -bits
            v = low.bit_length() - 1
            bits ^= low
            for w in adj[v]:
                if not (mask >> w) & 1:
                    reachable[mask | (1 << w)] |= (1 << w)
    bits = reachable[full]
    while bits:
        low = bits & -bits
        v = low.bit_length() - 1
        bits ^= low
        if v != 0 and 0 in adj[v]:
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(len(pairs) + 1):
        for chosen in itertools.combinations(pairs, r):
            yield {"n": n, "edges": [list(e) for e in chosen]}


def canonical(instance):
    n = instance["n"]
    edges = sorted(tuple(sorted(e)) for e in instance["edges"])
    return (n, tuple(edges))


def validate(instance):
    n = instance["n"]
    assert isinstance(n, int) and n >= 0
    seen = set()
    for e in instance["edges"]:
        assert isinstance(e, list) and len(e) == 2
        u, v = e
        assert isinstance(u, int) and isinstance(v, int)
        assert 0 <= u < n and 0 <= v < n
        assert u != v
        key = frozenset((u, v))
        assert key not in seen, f"duplicate edge {e}"
        seen.add(key)


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            src = solve_path(g)
            out = reduce(g)
            validate(out)
            tgt = solve_cycle(out)
            tests_run += 1
            if src == tgt:
                tests_passed += 1
            else:
                print("MISMATCH", g, "->", out, "src", src, "tgt", tgt)

    # A few larger random-ish structured cases.
    import random
    rng = random.Random(12345)
    for n in range(6, 10):
        for _ in range(300):
            pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
            edges = [list(e) for e in pairs if rng.random() < 0.4]
            g = {"n": n, "edges": edges}
            src = solve_path(g)
            out = reduce(g)
            validate(out)
            tgt = solve_cycle(out)
            tests_run += 1
            if src == tgt:
                tests_passed += 1
            else:
                print("MISMATCH", g, "->", out, "src", src, "tgt", tgt)

    # Specific edge cases.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},
    ]
    for g in edge_cases:
        src = solve_path(g)
        out = reduce(g)
        validate(out)
        tgt = solve_cycle(out)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            print("MISMATCH", g, "->", out, "src", src, "tgt", tgt)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
