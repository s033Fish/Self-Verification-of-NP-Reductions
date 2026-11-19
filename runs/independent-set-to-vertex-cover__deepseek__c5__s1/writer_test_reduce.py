"""Brute-force solvers and tests comparing IS answers with reduced VC answers."""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, VertexCover
from reduce import reduce


def is_independent(n, edges, subset):
    s = set(subset)
    for u, v in edges:
        if u in s and v in s:
            return False
    return True


def solve_is(instance):
    """Brute force: does the graph have an independent set of size >= k?"""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if is_independent(n, edges, subset):
                return True
    return False


def is_vertex_cover(n, edges, subset):
    s = set(subset)
    for u, v in edges:
        if u not in s and v not in s:
            return False
    return True


def solve_vc(instance):
    """Brute force: does the graph have a vertex cover of size <= k?"""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            if is_vertex_cover(n, edges, subset):
                return True
    return False


def random_graph(rng, n):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < 0.4:
                edges.append([u, v])
    return edges


def run_tests():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        IndependentSet.validate(instance)
        reduced = reduce(instance)
        VertexCover.validate(reduced)
        expected = solve_is(instance)
        got = solve_vc(reduced)
        assert expected == got, (
            f"MISMATCH: source={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )
        tests_passed += 1

    # Exhaustive small graphs with all k values, including edge cases.
    for n in range(0, 5):
        all_pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges = [list(p) for i, p in enumerate(all_pairs) if mask >> i & 1]
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random larger graphs.
    for _ in range(300):
        n = rng.randint(0, 9)
        edges = random_graph(rng, n)
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    return tests_run, tests_passed


if __name__ == "__main__":
    total, passed = run_tests()
    print(f"tests_run={total} tests_passed={passed}")
    assert total == passed
    print("ALL TESTS PASSED")
