"""Tests for the Hamiltonian Cycle -> Hamiltonian Path reduction.

We implement our own exact solvers (bitmask DP / Held-Karp) directly from
the definitions in problems.py and compare the answer of every small source
instance with the answer of its reduction.
"""

from __future__ import annotations

import random

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


# ----------------------------------------------------------------------
# Exact solvers (from the definitions, no solvers exist in problems.py)


def _adj_masks(instance):
    n = instance["n"]
    adj = [0] * n
    for u, v in instance["edges"]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return n, adj


def brute_hamiltonian_path(instance: dict) -> bool:
    n, adj = _adj_masks(instance)
    if n == 0:
        return False
    if n == 1:
        return True
    full = (1 << n) - 1
    # reachable[mask] = bitmask of endpoints of a simple path using exactly mask
    reachable = [0] * (1 << n)
    for v in range(n):
        reachable[1 << v] = 1 << v
    for mask in range(1 << n):
        ends = reachable[mask]
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
                reachable[mask | b] |= b
    return False


def brute_hamiltonian_cycle(instance: dict) -> bool:
    n, adj = _adj_masks(instance)
    if n <= 2:
        return False
    full = (1 << n) - 1
    # paths starting at vertex 0
    reachable = [0] * (1 << n)
    reachable[1] = 1
    for mask in range(1 << n):
        ends = reachable[mask]
        if not ends:
            continue
        e = ends
        while e:
            low = e & -e
            v = low.bit_length() - 1
            e ^= low
            if mask == full:
                if adj[v] & 1:
                    return True
                continue
            nxt = adj[v] & ~mask
            while nxt:
                b = nxt & -nxt
                w = b.bit_length() - 1
                nxt ^= b
                reachable[mask | b] |= b
    return False


# ----------------------------------------------------------------------
# Instance generation


def all_graphs(n: int):
    """Every simple undirected graph on n vertices (all edge subsets)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(e) for e in pairs if rng.random() < p]
    return {"n": n, "edges": edges}


def cycle_graph(n: int) -> dict:
    return {"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]}


def path_graph(n: int) -> dict:
    return {"n": n, "edges": [[i, i + 1] for i in range(n - 1)]}


# ----------------------------------------------------------------------


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianCycle.validate(instance)
        reduced = reduce(instance)
        HamiltonianPath.validate(reduced)
        expected = brute_hamiltonian_cycle(instance)
        got = brute_hamiltonian_path(reduced)
        assert expected == got, (
            f"MISMATCH source={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )
        tests_passed += 1

    # Exhaustive over all graphs with n = 0..5  (1100 instances)
    for n in range(0, 6):
        for instance in all_graphs(n):
            check(instance)

    # Random graphs for n = 6..9
    rng = random.Random(12345)
    for n in range(6, 10):
        for _ in range(300):
            check(random_graph(n, rng.random(), rng))

    # Larger structured / sparse / dense instances
    for n in range(10, 16):
        check(cycle_graph(n))                       # yes
        check(path_graph(n))                        # no
        check({"n": n, "edges": []})                # no
        edges = [[u, v] for u in range(n) for v in range(u + 1, n)]
        check({"n": n, "edges": edges})             # complete: yes
        extra = cycle_graph(n)["edges"] + [[0, 2]]
        check({"n": n, "edges": extra})             # cycle + chord: yes

    # Explicit edge cases
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})  # triangle: yes
    check({"n": 3, "edges": [[0, 1], [1, 2]]})           # path, no cycle
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})  # 4-cycle: yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})           # path: no

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
