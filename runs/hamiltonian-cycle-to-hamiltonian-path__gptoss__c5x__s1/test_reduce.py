"""Independent tests for reduce.py (Hamiltonian Cycle -> Hamiltonian Path).

Exact solvers are written directly from the problem definitions in
problems.py (bitmask DP, exponential but fast for the small instances used).
We compare the source answer with the target answer of the reduction over
many small instances (exhaustive for n <= 5, random for n = 6, 7) and also
check that the reduction returns a *valid* target instance.
"""

import itertools
import json
import random
import sys

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


# ----------------------------------------------------------------------
# Exact solvers, written from the definitions.

def _adj(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def ham_path(n, edges):
    """True iff some path visits every vertex exactly once (any endpoints)."""
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, edges)
    full = (1 << n) - 1
    # reachable[mask] = bitmask of vertices v such that a path ending at v
    # covers exactly the vertices in mask.
    reachable = [0] * (1 << n)
    for v in range(n):
        reachable[1 << v] = 1 << v
    for mask in range(1, 1 << n):
        ends = reachable[mask]
        if not ends:
            continue
        if mask == full:
            return True
        e = ends
        while e:
            v = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[v] & ~mask
            while nxt:
                u = (nxt & -nxt).bit_length() - 1
                nxt &= nxt - 1
                reachable[mask | (1 << u)] |= 1 << u
    return reachable[full] != 0


def ham_cycle(n, edges):
    """True iff some cycle visits every vertex exactly once and returns."""
    if n <= 2:
        return False
    adj = _adj(n, edges)
    full = (1 << n) - 1
    # paths starting at vertex 0
    reachable = [0] * (1 << n)
    reachable[1] = 1
    for mask in range(1, 1 << n):
        ends = reachable[mask]
        if not ends or not (mask & 1):
            continue
        e = ends
        while e:
            v = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[v] & ~mask
            while nxt:
                u = (nxt & -nxt).bit_length() - 1
                nxt &= nxt - 1
                reachable[mask | (1 << u)] |= 1 << u
    # a Hamiltonian cycle exists iff a Hamiltonian path from 0 ends at a
    # neighbor of 0.
    return (reachable[full] & adj[0]) != 0


# ----------------------------------------------------------------------
# Instance generation.

def all_graphs(n):
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = [list(e) for e in itertools.combinations(range(n), 2)
             if rng.random() < p]
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver.

def main():
    tests_run = 0
    tests_passed = 0
    mismatches = 0
    failures = []

    instances = []
    for n in range(0, 6):
        instances.extend(all_graphs(n))
    rng = random.Random(12345)
    for n in (6, 7):
        for _ in range(400):
            instances.append(random_graph(n, rng.choice([0.2, 0.4, 0.6, 0.8]), rng))

    for inst in instances:
        tests_run += 1
        try:
            HamiltonianCycle.validate(inst)
            src = ham_cycle(inst["n"], inst["edges"])
            red = reduce(inst)
            HamiltonianPath.validate(red)          # must be a valid target
            tgt = ham_path(red["n"], red["edges"])
        except Exception as exc:                    # invalid output / crash
            mismatches += 1
            if len(failures) < 5:
                failures.append((inst, "EXCEPTION", repr(exc), None))
            continue

        if src == tgt:
            tests_passed += 1
        else:
            mismatches += 1
            if len(failures) < 5:
                failures.append((inst, src, red, tgt))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for inst, src, red, tgt in failures:
        print("MISMATCH:")
        print("  source  :", inst, "-> source answer:", src)
        print("  reduced :", red, "-> target answer:", tgt)

    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("wrote verdict.json:", verdict)

    return tests_run, tests_passed, mismatches


if __name__ == "__main__":
    run, passed, nfail = main()
    sys.exit(0 if nfail == 0 else 1)
