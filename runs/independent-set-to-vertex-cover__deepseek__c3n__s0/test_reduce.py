"""Tests for the Independent Set -> Vertex Cover reduction in reduce.py.

Includes brute-force solvers written directly from the problem definitions
(problems.py has no solvers), an exhaustive check over all small graphs, and
randomized checks.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the definitions in problems.py.
# ----------------------------------------------------------------------

def is_independent_set(n, edges, chosen):
    chosen = set(chosen)
    for u, v in edges:
        if u in chosen and v in chosen:
            return False
    return True


def solve_independent_set(instance):
    """Yes iff some vertex set of size >= k is independent."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if is_independent_set(n, edges, subset):
                return True
    return False


def is_vertex_cover(n, edges, chosen):
    chosen = set(chosen)
    for u, v in edges:
        if u not in chosen and v not in chosen:
            return False
    return True


def solve_vertex_cover(instance):
    """Yes iff some vertex set of size <= k covers every edge."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            if is_vertex_cover(n, edges, subset):
                return True
    return False


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def all_graphs(n):
    """All simple undirected graphs on n vertices, as edge lists."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask & (1 << i)]
        yield edges


def check_instance(instance, stats):
    IndependentSet.validate(instance)
    out = reduce(instance)
    VertexCover.validate(out)

    src = solve_independent_set(instance)
    tgt = solve_vertex_cover(out)
    stats["tests_run"] += 1
    if src == tgt:
        stats["tests_passed"] += 1
    else:
        raise AssertionError(
            f"mismatch: source={instance} -> {src}, target={out} -> {tgt}"
        )
    return src, tgt


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_exhaustive_small_graphs():
    stats = {"tests_run": 0, "tests_passed": 0}
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                instance = {"n": n, "edges": [list(e) for e in edges], "k": k}
                check_instance(instance, stats)
    return stats


def test_no_edges():
    stats = {"tests_run": 0, "tests_passed": 0}
    for n in range(0, 7):
        for k in range(-2, n + 3):
            instance = {"n": n, "edges": [], "k": k}
            check_instance(instance, stats)
    return stats


def test_complete_graphs():
    stats = {"tests_run": 0, "tests_passed": 0}
    for n in range(0, 7):
        edges = [[u, v] for u in range(n) for v in range(u + 1, n)]
        for k in range(-2, n + 3):
            instance = {"n": n, "edges": [list(e) for e in edges], "k": k}
            check_instance(instance, stats)
    return stats


def test_random_graphs():
    stats = {"tests_run": 0, "tests_passed": 0}
    rng = random.Random(12345)
    for _ in range(600):
        n = rng.randint(0, 7)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.5:
                    edges.append([u, v])
        rng.shuffle(edges)
        k = rng.randint(-2, n + 2)
        instance = {"n": n, "edges": edges, "k": k}
        check_instance(instance, stats)
    return stats


def test_reduction_does_not_mutate_input():
    stats = {"tests_run": 0, "tests_passed": 0}
    instance = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
    snapshot = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
    out = reduce(instance)
    stats["tests_run"] += 1
    assert instance == snapshot, "reduce mutated its input"
    assert out["k"] == 2  # n - k = 4 - 2
    # Mutating the output must not affect the input.
    out["edges"].append([0, 2])
    out["edges"][0][0] = 99
    assert instance == snapshot, "output shares state with input"
    stats["tests_passed"] += 1
    return stats


def test_parameter_mapping():
    stats = {"tests_run": 0, "tests_passed": 0}
    for n in range(0, 10):
        for k in range(-3, n + 4):
            out = reduce({"n": n, "edges": [], "k": k})
            stats["tests_run"] += 1
            assert out["k"] == n - k, f"expected k'={n - k}, got {out['k']}"
            stats["tests_passed"] += 1
    return stats


def main():
    totals = {"tests_run": 0, "tests_passed": 0}
    tests = [
        ("exhaustive_small_graphs", test_exhaustive_small_graphs),
        ("no_edges", test_no_edges),
        ("complete_graphs", test_complete_graphs),
        ("random_graphs", test_random_graphs),
        ("reduction_does_not_mutate_input", test_reduction_does_not_mutate_input),
        ("parameter_mapping", test_parameter_mapping),
    ]
    for name, fn in tests:
        stats = fn()
        totals["tests_run"] += stats["tests_run"]
        totals["tests_passed"] += stats["tests_passed"]
        print(f"{name}: {stats['tests_passed']}/{stats['tests_run']} passed")
    print(f"TOTAL: {totals['tests_passed']}/{totals['tests_run']} passed")
    assert totals["tests_run"] == totals["tests_passed"], "some tests failed"
    return totals


if __name__ == "__main__":
    main()
