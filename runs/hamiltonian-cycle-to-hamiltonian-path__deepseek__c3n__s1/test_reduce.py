"""Brute-force verification of reduce.py on many small instances."""

from __future__ import annotations

import itertools
import json
import random

import problems
from reduce import reduce

SOURCE = problems.HamiltonianCycle
TARGET = problems.HamiltonianPath


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def _adj(n, edges):
    a = [[False] * n for _ in range(n)]
    for u, v in edges:
        a[u][v] = a[v][u] = True
    return a


def hamiltonian_path_yes(n, edges):
    if n == 0:
        return False
    if n == 1:
        return True
    adj = _adj(n, edges)
    full = (1 << n) - 1
    dp = [[False] * n for _ in range(1 << n)]
    for i in range(n):
        dp[1 << i][i] = True
    for mask in range(1 << n):
        row = dp[mask]
        for last in range(n):
            if row[last]:
                for nxt in range(n):
                    if not (mask >> nxt) & 1 and adj[last][nxt]:
                        dp[mask | (1 << nxt)][nxt] = True
    return any(dp[full][i] for i in range(n))


def hamiltonian_cycle_yes(n, edges):
    if n < 3:
        return False
    adj = _adj(n, edges)
    full = (1 << n) - 1
    dp = [[False] * n for _ in range(1 << n)]
    dp[1][0] = True
    for mask in range(1 << n):
        row = dp[mask]
        for last in range(n):
            if row[last]:
                for nxt in range(n):
                    if not (mask >> nxt) & 1 and adj[last][nxt]:
                        dp[mask | (1 << nxt)][nxt] = True
    return any(dp[full][last] and adj[last][0] for last in range(1, n))


# ----------------------------------------------------------------------
# Instance generation.

def all_graphs(n):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(len(possible) + 1):
        for chosen in itertools.combinations(possible, r):
            yield {"n": n, "edges": [list(e) for e in chosen]}


def random_graph(n, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < 0.5:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(instance)
        out = reduce(instance)
        TARGET.validate(out)
        expected = hamiltonian_cycle_yes(instance["n"], instance["edges"])
        got = hamiltonian_path_yes(out["n"], out["edges"])
        if expected == got:
            tests_passed += 1
        else:
            failures.append((instance, out, expected, got))

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for inst in all_graphs(n):
            check(inst)

    # Random larger instances.
    rng = random.Random(12345)
    for n in range(6, 10):
        for _ in range(400):
            check(random_graph(n, rng))

    # A few structured cases: cycles, paths, stars, complete graphs.
    for n in range(3, 11):
        cycle = {"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]}
        check(cycle)
        path = {"n": n, "edges": [[i, i + 1] for i in range(n - 1)]}
        check(path)
        star = {"n": n, "edges": [[0, i] for i in range(1, n)]}
        check(star)
        complete = {"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]}
        check(complete)

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:5]:
        print("FAIL", f)

    verified = tests_run == tests_passed and tests_run > 0
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
