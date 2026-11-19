"""Independent verification of reduce.py (Vertex Cover -> Dominating Set).

Brute-force / branch-and-bound solvers for both problems are written directly
from the definitions in problems.py.  We enumerate many small instances,
reduce each one, validate the produced target instance, and compare answers.
"""

from __future__ import annotations

import random
import sys
from typing import Any

from problems import SOURCE, TARGET
from reduce import reduce

sys.setrecursionlimit(100000)


# ----------------------------------------------------------------------
# Exact solvers (from the definitions, not from reduce.py)

def min_vertex_cover(n: int, edges: list[list[int]]) -> int:
    """Exact minimum vertex cover size via branch and bound."""
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    edge_list = [(u, v) for u, v in edges]

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def solve(covered_edges_mask: int) -> int:
        # find first uncovered edge
        remaining = covered_edges_mask
        if remaining == 0:
            return 0
        i = (remaining & -remaining).bit_length() - 1
        u, v = edge_list[i]
        best = None
        for c in (u, v):
            # cover all edges incident to c
            new = remaining
            for j, (a, b) in enumerate(edge_list):
                if (new >> j) & 1 and (a == c or b == c):
                    new &= ~(1 << j)
            sub = 1 + solve(new)
            if best is None or sub < best:
                best = sub
        return best

    full = (1 << len(edge_list)) - 1
    return solve(full)


def min_dominating_set(n: int, edges: list[list[int]]) -> int:
    """Exact minimum dominating set size via branch and bound + memoization."""
    closed = [1 << i for i in range(n)]  # closed neighbourhood masks
    for u, v in edges:
        closed[u] |= 1 << v
        closed[v] |= 1 << u
    full = (1 << n) - 1

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def solve(dominated: int) -> int:
        if dominated == full:
            return 0
        # lowest undominated vertex
        undom = (~dominated) & full
        v = (undom & -undom).bit_length() - 1
        # to dominate v we must pick v or one of its neighbours
        candidates = [i for i in range(n) if (closed[v] >> i) & 1]
        best = None
        for c in candidates:
            sub = 1 + solve(dominated | closed[c])
            if best is None or sub < best:
                best = sub
        return best

    return solve(0)


def solve_vc(instance: dict[str, Any]) -> bool:
    n, k = instance["n"], instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    return min_vertex_cover(n, instance["edges"]) <= k


def solve_ds(instance: dict[str, Any]) -> bool:
    n, k = instance["n"], instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    return min_dominating_set(n, instance["edges"]) <= k


# ----------------------------------------------------------------------
# Enumeration / test driver

def all_graphs(n: int):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        yield [list(e) for i, e in enumerate(possible) if mask & (1 << i)]


def run() -> tuple[int, int, list[str]]:
    tests_run = 0
    tests_passed = 0
    failures: list[str] = []

    def check(instance: dict[str, Any], label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)  # must be a well-formed target instance
        expected = solve_vc(instance)
        got = solve_ds(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append(
                f"{label}: source={instance} expected={expected} "
                f"reduced={reduced} got={got}"
            )

    # Exhaustive over all graphs on 0..5 vertices and a range of k values.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-1, n + 2):
                check({"n": n, "edges": edges, "k": k}, f"exhaustive n={n}")

    # Random instances, including isolated vertices and disconnected graphs.
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 8)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(possible)
        m = rng.randint(0, len(possible))
        edges = [list(e) for e in possible[:m]]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k}, "random")

    # Targeted: isolated vertices only, empty graph, single edges.
    for n in range(0, 8):
        for k in range(-1, n + 2):
            check({"n": n, "edges": [], "k": k}, "empty")
            if n >= 2:
                check({"n": n, "edges": [[0, 1]], "k": k}, "single-edge")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = run()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print(" ", f)
    else:
        print("all tests passed")
