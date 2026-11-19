"""Tests for reduce.py: brute-force solvers + exhaustive small-instance check."""

from __future__ import annotations

import json
import random

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (Held-Karp bitmask DP) from the definitions.

def brute_hamiltonian_path(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    full = (1 << n) - 1
    # reachable[mask] = bitmask of possible endpoints of a path covering mask
    reachable = [0] * (1 << n)
    for i in range(n):
        reachable[1 << i] = 1 << i
    for mask in range(1, 1 << n):
        ends = reachable[mask]
        if not ends:
            continue
        e = ends
        while e:
            last = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[last] & ~mask
            while nxt:
                b = nxt & -nxt
                reachable[mask | b] |= b
                nxt &= nxt - 1
    return reachable[full] != 0


def brute_hamiltonian_cycle(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    full = (1 << n) - 1
    # paths starting at vertex 0
    reachable = [0] * (1 << n)
    reachable[1] = 1
    for mask in range(1, 1 << n):
        ends = reachable[mask]
        if not ends:
            continue
        e = ends
        while e:
            last = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[last] & ~mask
            while nxt:
                b = nxt & -nxt
                reachable[mask | b] |= b
                nxt &= nxt - 1
    # cycle iff some Hamiltonian path from 0 ends at a neighbour of 0
    ends = reachable[full]
    return bool(ends & adj[0])


# ----------------------------------------------------------------------
# Helpers.

def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def check(instance: dict) -> None:
    HamiltonianCycle.validate(instance)
    src = brute_hamiltonian_cycle(instance)
    out = reduce(instance)
    HamiltonianPath.validate(out)
    tgt = brute_hamiltonian_path(out)
    assert src == tgt, f"MISMATCH src={src} tgt={tgt}\n{instance}\n{out}"


def main() -> None:
    tests_run = 0
    tests_passed = 0

    # 1. Exhaustive over all simple graphs with n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            tests_run += 1
            check(g)
            tests_passed += 1

    # 2. Random graphs with n = 6..9.
    rng = random.Random(12345)
    for n in range(6, 10):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(500):
            p = rng.random()
            edges = [list(e) for e in pairs if rng.random() < p]
            tests_run += 1
            check({"n": n, "edges": edges})
            tests_passed += 1

    # 3. Hand-picked structured cases.
    hand = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]]},
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]},
    ]
    for g in hand:
        tests_run += 1
        check(g)
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)


if __name__ == "__main__":
    main()
