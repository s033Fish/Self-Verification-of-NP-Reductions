"""Independent verification of reduce.py: 3-Coloring -> Independent Set.

We write our own exact solvers for both problems from the definitions in
problems.py, then compare the answer on small source instances against the
answer on their reductions.  Exhaustive for n = 0..4, random sampling for
n = 5..8, plus targeted edge cases and a polynomial-time sanity check.
"""

from __future__ import annotations

import random
import time

from problems import ThreeColoring, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Exact solvers written from the definitions.

def solve_three_coloring(instance: dict) -> bool:
    """Yes iff the graph is properly 3-colourable (backtracking)."""
    ThreeColoring.validate(instance)
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n

    def rec(v: int) -> bool:
        if v == n:
            return True
        for c in range(3):
            if all(color[w] != c for w in adj[v]):
                color[v] = c
                if rec(v + 1):
                    return True
                color[v] = -1
        return False

    return rec(0)


def solve_independent_set(instance: dict) -> bool:
    """Yes iff there is an independent set of size >= k.

    Exact branch-and-bound maximum-independent-set search.
    """
    IndependentSet.validate(instance)
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [0] * n
    for u, v in instance["edges"]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u

    best = 0

    def rec(candidates: int, size: int) -> None:
        nonlocal best
        if size >= k:
            best = size
            return
        if size + bin(candidates).count("1") < k:
            return
        if candidates == 0:
            if size > best:
                best = size
            return
        v = max(
            (i for i in range(n) if (candidates >> i) & 1),
            key=lambda i: bin(adj[i] & candidates).count("1"),
        )
        rec(candidates & ~(adj[v] | (1 << v)), size + 1)
        rec(candidates & ~(1 << v), size)

    rec((1 << n) - 1, 0)
    return best >= k


# ----------------------------------------------------------------------
# Instance generation.

def all_graphs(n: int):
    """All undirected simple graphs on n vertices, as 3-Coloring instances."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = [[u, v] for u in range(n) for v in range(u + 1, n) if rng.random() < p]
    return {"n": n, "edges": edges}


def check(src: dict, failures: list) -> bool:
    """Return True if reduction agrees with the source solver."""
    expected = solve_three_coloring(src)
    tgt = reduce(src)
    IndependentSet.validate(tgt)          # must be a well-formed target instance
    got = solve_independent_set(tgt)
    if got != expected:
        failures.append((src, expected, tgt, got))
        return False
    return True


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures: list = []

    # 1. Exhaustive over all graphs with n = 0..4.
    for n in range(0, 5):
        for src in all_graphs(n):
            tests_run += 1
            if check(src, failures):
                tests_passed += 1

    # 2. Random sampling for n = 5..8.
    rng = random.Random(12345)
    for n in range(5, 9):
        for p in (0.0, 0.15, 0.3, 0.5, 0.7, 1.0):
            for _ in range(25):
                src = random_graph(n, p, rng)
                tests_run += 1
                if check(src, failures):
                    tests_passed += 1

    # 3. Targeted edge cases.
    extra = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},          # K3, yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},  # C4, yes
        {"n": 4, "edges": [[i, j] for i in range(4) for j in range(i + 1, 4)]},  # K4, no
        {"n": 5, "edges": [[i, (i + 1) % 5] for i in range(5)]},  # C5, no
        {"n": 6, "edges": [[i, (i + 1) % 6] for i in range(6)]},  # C6, yes
        {"n": 9, "edges": [[i, (i + 1) % 9] for i in range(9)]},  # C9, no
        {"n": 10, "edges": [[i, (i + 1) % 10] for i in range(10)]},  # C10, yes
    ]
    for src in extra:
        tests_run += 1
        if check(src, failures):
            tests_passed += 1

    # 4. Reduction output size / polynomial-time sanity on a large instance.
    big = {"n": 2000, "edges": [[i, i + 1] for i in range(1999)]}
    t0 = time.time()
    out = reduce(big)
    elapsed = time.time() - t0
    tests_run += 1
    size_ok = out["n"] == 3 * 2000 and out["k"] == 2000
    time_ok = elapsed < 10.0
    if size_ok and time_ok:
        tests_passed += 1
    else:
        failures.append(("large instance size/time", size_ok, time_ok, elapsed))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for src, expected, tgt, got in failures[:10]:
        print("MISMATCH", src, "expected", expected, "got", got, "reduced", tgt)

    assert not failures, f"{len(failures)} mismatches"
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
