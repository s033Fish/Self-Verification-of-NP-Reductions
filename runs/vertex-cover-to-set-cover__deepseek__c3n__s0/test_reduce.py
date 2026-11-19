"""Tests for the Vertex Cover -> Set Cover reduction.

Includes brute-force solvers for both problems written from the definitions
in problems.py, and compares answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from reduce import reduce
import problems


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)

def solve_vertex_cover(instance: dict) -> bool:
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
        for chosen in itertools.combinations(range(n), size):
            cover = set(chosen)
            if all(u in cover or v in cover for u, v in edges):
                return True
    return False


def solve_set_cover(instance: dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return k >= 0
    # Any element in no set -> impossible.
    available = set()
    for s in sets:
        available.update(s)
    if available != set(range(u)):
        return False
    if k >= len(sets):
        return True
    for size in range(0, k + 1):
        for chosen in itertools.combinations(range(len(sets)), size):
            covered = set()
            for i in chosen:
                covered.update(sets[i])
            if len(covered) == u:
                return True
    return False


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n):
    """All simple undirected graphs on n labelled vertices."""
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield edges


def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Both instances must validate.
        problems.SOURCE.validate(instance)
        target = reduce(instance)
        problems.TARGET.validate(target)
        expected = solve_vertex_cover(instance)
        got = solve_set_cover(target)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, target, expected, got))

    # Exhaustive small graphs, n = 0..4, k in -2..n+1.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 2):
                check({"n": n, "edges": edges, "k": k}, f"exhaustive n={n}")

    # Random slightly larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 7)
        possible = list(itertools.combinations(range(n), 2))
        rng.shuffle(possible)
        m = rng.randint(0, len(possible))
        edges = [list(e) for e in possible[:m]]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k}, "random")

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0}, "empty graph k=0")
    check({"n": 0, "edges": [], "k": -1}, "empty graph k=-1")
    check({"n": 5, "edges": [], "k": 0}, "no edges k=0")
    check({"n": 5, "edges": [], "k": -1}, "no edges k=-1")
    check({"n": 3, "edges": [[0, 1]], "k": 0}, "one edge k=0")
    check({"n": 3, "edges": [[0, 1]], "k": 1}, "one edge k=1")
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}, "two disjoint edges k=1")
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, "two disjoint edges k=2")
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 1}, "path k=1")
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2}, "path k=2")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, "triangle k=1")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, "triangle k=2")
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 1}, "star k=1")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = run_tests()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for label, instance, target, expected, got in failures[:10]:
        print("FAIL", label, instance, "->", target, "expected", expected, "got", got)
    assert not failures, f"{len(failures)} failures"
    print("ALL TESTS PASSED")
