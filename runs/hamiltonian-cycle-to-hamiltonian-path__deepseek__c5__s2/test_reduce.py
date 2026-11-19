"""Independent tests for reduce.py (HamiltonianCycle -> HamiltonianPath).

We implement our own exact solvers directly from the problem definitions
(bitmask dynamic programming, no external solvers), then compare source
answers with target answers of the reduction on many small instances.
"""

from __future__ import annotations

import json
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Exact solvers written from the docstrings (Held-Karp style DP)


def _adjmask(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def solve_hamiltonian_cycle(instance):
    """Yes iff there is a cycle through every vertex exactly once."""
    n = instance["n"]
    if n < 3:
        return False
    adj = _adjmask(n, instance["edges"])
    # Fix vertex 0 as the start. dp[mask][v]: a path 0 -> ... -> v using
    # exactly the vertices in mask (mask always includes bit 0).
    full = (1 << n) - 1
    dp = [0] * (1 << n)
    dp[1] = 1  # only vertex 0 reachable, stored as bit 0
    # Represent reachable endpoints as a bitmask for speed.
    reach = [0] * (1 << n)
    reach[1] = 1  # endpoint 0
    for mask in range(1, 1 << n, 2):  # masks containing bit 0
        ends = reach[mask]
        if not ends:
            continue
        e = ends
        while e:
            v = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[v] & ~mask
            while nxt:
                w = (nxt & -nxt).bit_length() - 1
                nxt &= nxt - 1
                reach[mask | (1 << w)] |= 1 << w
    ends = reach[full]
    e = ends
    while e:
        v = (e & -e).bit_length() - 1
        e &= e - 1
        if v != 0 and (adj[v] >> 0) & 1:
            return True
    return False


def solve_hamiltonian_path(instance):
    """Yes iff there is a path through every vertex exactly once."""
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adjmask(n, instance["edges"])
    reach = [0] * (1 << n)
    for v in range(n):
        reach[1 << v] = 1 << v
    for mask in range(1, 1 << n):
        ends = reach[mask]
        if not ends:
            continue
        e = ends
        while e:
            v = (e & -e).bit_length() - 1
            e &= e - 1
            nxt = adj[v] & ~mask
            while nxt:
                w = (nxt & -nxt).bit_length() - 1
                nxt &= nxt - 1
                reach[mask | (1 << w)] |= 1 << w
    return reach[(1 << n) - 1] != 0


# ----------------------------------------------------------------------
# Instance generation


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, rng):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            SOURCE.validate(inst)
        except Exception as exc:  # pragma: no cover
            failures.append((inst, "source invalid: %r" % (exc,)))
            return
        src = solve_hamiltonian_cycle(inst)
        out = reduce(inst)
        try:
            TARGET.validate(out)
        except Exception as exc:
            failures.append((inst, "reduced instance invalid: %r" % (exc,)))
            return
        tgt = solve_hamiltonian_path(out)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, "src=%s tgt=%s reduced=%r" % (src, tgt, out)))

    # Exhaustive over all graphs for n = 0..7
    for n in range(0, 7):
        for inst in all_graphs(n):
            check(inst)

    # Random larger instances
    rng = random.Random(12345)
    for n in range(7, 13):
        for _ in range(200):
            check(random_graph(n, rng))

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    print("failures =", len(failures))
    for inst, msg in failures[:20]:
        print("FAIL:", inst, "->", msg)

    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": len(failures) == 0 and tests_run > 0,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
            },
            fh,
        )
        fh.write("\n")


if __name__ == "__main__":
    main()
