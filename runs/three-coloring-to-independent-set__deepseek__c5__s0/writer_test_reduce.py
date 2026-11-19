"""Brute-force solvers and tests comparing 3-Coloring with its reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force / exact solvers written from the problem definitions.

def solve_three_coloring(instance: dict) -> bool:
    """Brute force: try all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def max_independent_set(n: int, edges: list) -> int:
    """Exact maximum independent set size via branch and bound."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    best = 0

    def rec(candidates: set, current: int) -> None:
        nonlocal best
        if current + len(candidates) <= best:
            return
        if not candidates:
            if current > best:
                best = current
            return
        v = max(candidates, key=lambda x: len(adj[x] & candidates))
        rest = candidates - {v}
        # Exclude v.
        rec(rest, current)
        # Include v.
        rec(rest - adj[v], current + 1)

    rec(set(range(n)), 0)
    return best


def solve_independent_set(instance: dict) -> bool:
    """Yes iff the graph has an independent set of size >= k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    return max_independent_set(n, instance["edges"]) >= k


# ----------------------------------------------------------------------
# Instance generators.

def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def all_graphs(n: int):
    """Yield every simple graph on n vertices (all edge subsets)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def run_tests() -> tuple[int, int]:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeColoring.validate(instance)
        reduced = reduce(instance)
        IndependentSet.validate(reduced)
        source_ans = solve_three_coloring(instance)
        target_ans = solve_independent_set(reduced)
        assert source_ans == target_ans, (
            f"mismatch on {instance}: source={source_ans}, target={target_ans}, "
            f"reduced={reduced}"
        )
        tests_passed += 1

    # Exhaustive over all graphs with up to 5 vertices (covers K4 = no case).
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(500):
        n = rng.randint(0, 9)
        p = rng.choice([0.0, 0.1, 0.3, 0.5, 0.8, 1.0])
        check(random_graph(n, p, rng))

    # A few explicit edge cases.
    check({"n": 0, "edges": []})                       # yes
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})  # triangle: yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]})  # K4: no
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})  # C5: yes

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed
