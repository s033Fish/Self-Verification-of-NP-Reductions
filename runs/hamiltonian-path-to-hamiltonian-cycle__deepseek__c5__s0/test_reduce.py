"""Independent tests for reduce.py: Hamiltonian Path -> Hamiltonian Cycle.

We implement brute-force solvers from the problem definitions, then compare
answers on many small source instances (exhaustive over all graphs for small n)
and their reductions.
"""

from __future__ import annotations

import itertools
import sys

import problems
from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstrings)

def _adj(n, edges):
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def hp_solver(instance):
    """Yes iff there is a Hamiltonian path (any endpoints)."""
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, edges)
    for perm in itertools.permutations(range(n)):
        if all(perm[i + 1] in adj[perm[i]] for i in range(n - 1)):
            return True
    return False


def hc_solver(instance):
    """Yes iff there is a Hamiltonian cycle."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = _adj(n, edges)
    # Fix the first vertex to 0 to avoid rotational duplicates.
    for perm in itertools.permutations(range(1, n)):
        cycle = (0,) + perm
        ok = all(cycle[i + 1] in adj[cycle[i]] for i in range(n - 1))
        if ok and cycle[0] in adj[cycle[-1]]:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    """Yield every valid graph instance on n vertices (undirected, no loops)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    # Exhaustive over all graphs for n = 0..6.
    for n in range(0, 7):
        for inst in all_graphs(n):
            tests_run += 1
            try:
                HamiltonianPath.validate(inst)
            except Exception as exc:  # pragma: no cover
                failures.append(("source invalid", inst, repr(exc)))
                continue

            expected = hp_solver(inst)
            red = reduce(inst)

            # Reduction output must be a valid target instance.
            try:
                HamiltonianCycle.validate(red)
            except Exception as exc:
                failures.append(("target invalid", inst, red, repr(exc)))
                continue

            got = hc_solver(red)
            if got == expected:
                tests_passed += 1
            else:
                failures.append(("mismatch", inst, red, expected, got))

    # A few larger random-ish structured cases for sanity (n = 7, 8).
    import random
    rng = random.Random(12345)
    for n in (7, 8):
        for _ in range(200):
            pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
            edges = [list(p) for p in pairs if rng.random() < 0.5]
            inst = {"n": n, "edges": edges}
            tests_run += 1
            expected = hp_solver(inst)
            red = reduce(inst)
            try:
                HamiltonianCycle.validate(red)
            except Exception as exc:
                failures.append(("target invalid", inst, red, repr(exc)))
                continue
            got = hc_solver(red)
            if got == expected:
                tests_passed += 1
            else:
                failures.append(("mismatch", inst, red, expected, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  ", f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
