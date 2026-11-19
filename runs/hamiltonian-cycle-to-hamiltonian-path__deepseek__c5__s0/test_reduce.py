"""Independent verification of reduce.py (Hamiltonian Cycle -> Hamiltonian Path).

We implement our own brute-force solvers from the problem definitions using
bitmask DP (exact, exponential but fine for small n), then compare the source
answer with the target answer of the reduction on many small instances.
"""
import itertools
import random

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (bitmask DP), written from the definitions.
# ----------------------------------------------------------------------

def _adj(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def solve_hamiltonian_cycle(instance):
    """Yes iff there is a cycle visiting every vertex exactly once."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = _adj(n, edges)
    full = (1 << n) - 1
    # dp[mask][v]: path starting at 0, visiting exactly mask, ending at v.
    dp = [[False] * n for _ in range(1 << n)]
    dp[1][0] = True
    for mask in range(1 << n):
        if not (mask & 1):
            continue
        for v in range(n):
            if not dp[mask][v]:
                continue
            nbrs = adj[v]
            for w in range(n):
                if nbrs >> w & 1 and not (mask >> w & 1):
                    dp[mask | (1 << w)][w] = True
    for v in range(n):
        if dp[full][v] and (adj[v] >> 0 & 1):
            return True
    return False


def solve_hamiltonian_path(instance):
    """Yes iff there is a path visiting every vertex exactly once."""
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, edges)
    full = (1 << n) - 1
    dp = [[False] * n for _ in range(1 << n)]
    for v in range(n):
        dp[1 << v][v] = True
    for mask in range(1 << n):
        for v in range(n):
            if not dp[mask][v]:
                continue
            nbrs = adj[v]
            for w in range(n):
                if nbrs >> w & 1 and not (mask >> w & 1):
                    dp[mask | (1 << w)][w] = True
    return any(dp[full][v] for v in range(n))


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    """All simple undirected graphs on n vertices, as edge lists."""
    pairs = list(itertools.combinations(range(n), 2))
    for bits in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if bits >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, rng):
    pairs = list(itertools.combinations(range(n), 2))
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        HamiltonianCycle.validate(inst)
        src = solve_hamiltonian_cycle(inst)
        out = reduce(inst)
        # reduced instance must be a valid target instance
        HamiltonianPath.validate(out)
        tgt = solve_hamiltonian_path(out)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, src, out, tgt))

    # Exhaustive over all graphs for n = 0..6
    for n in range(0, 7):
        for inst in all_graphs(n):
            check(inst)

    # Random larger instances
    rng = random.Random(12345)
    for n in range(7, 10):
        for _ in range(300):
            check(random_graph(n, rng))

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:10]:
        print("FAIL:", f)

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
