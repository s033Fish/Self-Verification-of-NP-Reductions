"""Tests for reduce.py: brute-force solvers + exhaustive small-instance checks."""

from __future__ import annotations

import itertools
import random
from functools import lru_cache

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def solve_three_coloring(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


def solve_independent_set(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adjmask = [0] * n
    for u, v in edges:
        adjmask[u] |= 1 << v
        adjmask[v] |= 1 << u

    @lru_cache(maxsize=None)
    def mis(mask: int) -> int:
        if mask == 0:
            return 0
        v = (mask & -mask).bit_length() - 1
        without_v = mask & ~(1 << v)
        return max(mis(without_v), 1 + mis(without_v & ~adjmask[v]))

    return mis((1 << n) - 1) >= k


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n: int):
    """All simple undirected graphs on n labelled vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests

tests_run = 0
tests_passed = 0


def check(condition: bool, message: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        raise AssertionError(message)


def verify(instance: dict) -> None:
    problems.ThreeColoring.validate(instance)
    reduced = reduce(instance)
    problems.IndependentSet.validate(reduced)
    expected = solve_three_coloring(instance)
    got = solve_independent_set(reduced)
    check(
        expected == got,
        f"mismatch for {instance}: source={expected}, target={got}, reduced={reduced}",
    )


def main() -> None:
    # Edge cases from the docstrings.
    verify({"n": 0, "edges": []})
    for n in range(0, 4):
        for g in all_graphs(n):
            verify(g)

    # Exhaustive over all graphs on up to 5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            verify(g)

    # Random larger graphs.
    rng = random.Random(12345)
    for n in range(6, 9):
        for _ in range(40):
            verify(random_graph(n, rng.uniform(0.1, 0.9), rng))

    # Explicit K4 is a no-instance; K3 is a yes-instance.
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    verify(k4)
    check(solve_three_coloring(k4) is False, "K4 must be no")
    k3 = {"n": 3, "edges": [[0, 1], [0, 2], [1, 2]]}
    verify(k3)
    check(solve_three_coloring(k3) is True, "K3 must be yes")

    # Reduction must be polynomial-sized: n' = 3n, k = n.
    for n in range(0, 8):
        g = random_graph(n, 0.5, rng)
        r = reduce(g)
        check(r["n"] == 3 * n, "target n must be 3*source n")
        check(r["k"] == n, "target k must be source n")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
