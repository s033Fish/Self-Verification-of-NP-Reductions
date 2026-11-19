"""Tests for the 3-Coloring -> Independent Set reduction.

Includes brute-force solvers written directly from the problem
definitions in problems.py, plus an exhaustive comparison of solver
answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the definitions in problems.py)

def solve_three_coloring(instance: dict) -> bool:
    """Brute force: try all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colouring[u] == colouring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def max_independent_set(n: int, edges: list) -> int:
    """Exact maximum independent set size via branch and bound."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    best = 0

    def rec(candidates: set, size: int) -> None:
        nonlocal best
        if size + len(candidates) <= best:
            return
        if not candidates:
            if size > best:
                best = size
            return
        # Branch on the candidate with the most conflicts.
        v = max(candidates, key=lambda x: len(adj[x] & candidates))
        # Include v.
        rec(candidates - {v} - adj[v], size + 1)
        # Exclude v.
        rec(candidates - {v}, size)

    rec(set(range(n)), 0)
    return best


def solve_independent_set(instance: dict) -> bool:
    """Yes iff there is an independent set of at least k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    return max_independent_set(n, instance["edges"]) >= k


# ----------------------------------------------------------------------
# Instance generators

def all_graphs(n: int):
    """Yield every simple undirected graph on n vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < 0.5:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests

def test_reduction_matches_on_all_small_graphs():
    """Exhaustively check every graph on 0..5 vertices."""
    tests = 0
    for n in range(0, 6):
        for source in all_graphs(n):
            ThreeColoring.validate(source)
            target = reduce(source)
            IndependentSet.validate(target)
            expected = solve_three_coloring(source)
            got = solve_independent_set(target)
            assert got == expected, (source, target, expected, got)
            tests += 1
    return tests


def test_reduction_matches_on_random_graphs():
    rng = random.Random(12345)
    tests = 0
    for _ in range(500):
        n = rng.randint(0, 9)
        source = random_graph(n, rng)
        ThreeColoring.validate(source)
        target = reduce(source)
        IndependentSet.validate(target)
        expected = solve_three_coloring(source)
        got = solve_independent_set(target)
        assert got == expected, (source, target, expected, got)
        tests += 1
    return tests


def test_known_edge_cases():
    tests = 0

    # n = 0 is yes.
    source = {"n": 0, "edges": []}
    assert solve_three_coloring(source) is True
    assert solve_independent_set(reduce(source)) is True
    tests += 1

    # Any graph with at most 3 vertices is yes.
    for n in range(0, 4):
        for source in all_graphs(n):
            assert solve_three_coloring(source) is True
            assert solve_independent_set(reduce(source)) is True
            tests += 1

    # K4 is no.
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    assert solve_three_coloring(k4) is False
    assert solve_independent_set(reduce(k4)) is False
    tests += 1

    # C5 is 3-colourable (yes).
    c5 = {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}
    assert solve_three_coloring(c5) is True
    assert solve_independent_set(reduce(c5)) is True
    tests += 1

    # K5 is no.
    k5 = {"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]}
    assert solve_three_coloring(k5) is False
    assert solve_independent_set(reduce(k5)) is False
    tests += 1

    return tests


def test_target_edge_cases_are_consistent():
    """The reduction always produces k = n, and the target handles k edge cases."""
    tests = 0
    source = {"n": 0, "edges": []}
    target = reduce(source)
    assert target["k"] == 0
    assert solve_independent_set(target) is True
    tests += 1
    return tests


def main():
    total = 0
    passed = 0
    for fn in [
        test_reduction_matches_on_all_small_graphs,
        test_reduction_matches_on_random_graphs,
        test_known_edge_cases,
        test_target_edge_cases_are_consistent,
    ]:
        count = fn()
        total += count
        passed += count
        print(f"{fn.__name__}: {count} checks passed")
    print(f"TOTAL: {passed}/{total} checks passed")
    return passed, total


if __name__ == "__main__":
    main()
