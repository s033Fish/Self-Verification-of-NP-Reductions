"""Tests for reduce.py: compare brute-force answers on source instances."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


def has_hamiltonian_path(n, edges):
    if n == 0:
        return False
    if n == 1:
        return True
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for perm in itertools.permutations(range(n)):
        if all(adj[perm[i]][perm[i + 1]] for i in range(n - 1)):
            return True
    return False


def has_hamiltonian_cycle(n, edges):
    if n <= 2:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    start = 0
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        order = (start,) + perm
        if all(adj[order[i]][order[(i + 1) % n]] for i in range(n)):
            return True
    return False


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        yield [[u, v] for i, (u, v) in enumerate(pairs) if mask >> i & 1]


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for edges in all_graphs(n):
            inst = {"n": n, "edges": edges}
            HamiltonianPath.validate(inst)
            src = has_hamiltonian_path(n, edges)
            out = reduce(inst)
            HamiltonianCycle.validate(out)
            tgt = has_hamiltonian_cycle(out["n"], out["edges"])
            tests_run += 1
            if src == tgt:
                tests_passed += 1
            else:
                print("FAIL", inst, "->", out, "src", src, "tgt", tgt)
                raise SystemExit(1)

    # Random larger graphs n = 6..8.
    rng = random.Random(12345)
    for n in range(6, 9):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(400):
            edges = [list(p) for p in pairs if rng.random() < 0.4]
            inst = {"n": n, "edges": edges}
            HamiltonianPath.validate(inst)
            src = has_hamiltonian_path(n, edges)
            out = reduce(inst)
            HamiltonianCycle.validate(out)
            tgt = has_hamiltonian_cycle(out["n"], out["edges"])
            tests_run += 1
            if src == tgt:
                tests_passed += 1
            else:
                print("FAIL", inst, "->", out, "src", src, "tgt", tgt)
                raise SystemExit(1)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
    print("wrote verdict.json")


if __name__ == "__main__":
    main()
