"""Brute-force (bitmask DP) solvers and tests for the HC -> HP reduction."""

import itertools
import random
import sys

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


def _adj(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def has_hamiltonian_cycle(instance):
    """Exact: is there a Hamiltonian cycle? (bitmask DP, start at 0)."""
    n = instance["n"]
    if n <= 2:
        return False
    adj = _adj(n, instance["edges"])
    # reach[mask] = set of vertices v such that a path from 0 visiting
    # exactly mask and ending at v exists (0 in mask).
    reach = [0] * (1 << n)
    reach[1] = 1  # path {0} ending at 0
    for mask in range(1 << n):
        ends = reach[mask]
        if not ends:
            continue
        e = ends
        while e:
            v = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[v] & ~mask
            while nxt:
                u = (nxt & -nxt).bit_length() - 1
                nxt &= nxt - 1
                reach[mask | (1 << u)] |= 1 << u
    full = (1 << n) - 1
    ends = reach[full]
    while ends:
        v = (ends & -ends).bit_length() - 1
        ends &= ends - 1
        if adj[v] & 1:
            return True
    return False


def has_hamiltonian_path(instance):
    """Exact: is there a Hamiltonian path? (bitmask DP)."""
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, instance["edges"])
    reach = [0] * (1 << n)
    for v in range(n):
        reach[1 << v] |= 1 << v
    for mask in range(1 << n):
        ends = reach[mask]
        if not ends:
            continue
        e = ends
        while e:
            v = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[v] & ~mask
            while nxt:
                u = (nxt & -nxt).bit_length() - 1
                nxt &= nxt - 1
                reach[mask | (1 << u)] |= 1 << u
    return reach[(1 << n) - 1] != 0


def all_graphs(n):
    """All simple undirected graphs on n labelled vertices."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianCycle.validate(instance)
        out = reduce(instance)
        HamiltonianPath.validate(out)
        src = has_hamiltonian_cycle(instance)
        tgt = has_hamiltonian_path(out)
        if src == tgt:
            tests_passed += 1
        else:
            print("FAIL", instance, "->", out, "src", src, "tgt", tgt)
        return src == tgt

    # Exhaustive over all graphs for n = 0..6.
    for n in range(0, 7):
        for g in all_graphs(n):
            check(g)

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(2000):
        n = rng.randint(0, 10)
        pairs = list(itertools.combinations(range(n), 2))
        p = rng.choice([0.1, 0.2, 0.3, 0.5, 0.8])
        edges = [list(pp) for pp in pairs if rng.random() < p]
        check({"n": n, "edges": edges})

    # Structured graphs.
    for n in range(1, 12):
        check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)] if n >= 3 else []})
        check({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]})
        check({"n": n, "edges": [list(p) for p in itertools.combinations(range(n), 2)]})
        # cycle plus a chord
        e = [[i, (i + 1) % n] for i in range(n)] if n >= 3 else []
        if n >= 4:
            e = e + [[0, 2]]
        check({"n": n, "edges": e})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = main()
    sys.exit(0 if run == passed else 1)
