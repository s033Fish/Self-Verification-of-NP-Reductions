"""Independent verification of reduce.py: Vertex Cover -> Independent Set.

We write brute-force solvers for both problems from the definitions in
problems.py, then compare answers on many small source instances and their
reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstring definitions)

def solve_vertex_cover(instance) -> bool:
    """Yes iff some vertex subset of size <= k covers every edge."""
    SOURCE.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    vertices = range(n)
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_independent_set(instance) -> bool:
    """Yes iff some vertex subset of size >= k has no internal edge."""
    TARGET.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = range(n)
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            chosen = set(subset)
            if all(not (u in chosen and v in chosen) for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    """All simple undirected graphs on n labelled vertices (as edge lists)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return edges


# ----------------------------------------------------------------------
# Tests

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(vc_instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = solve_vertex_cover(vc_instance)
        try:
            reduced = reduce(vc_instance)
        except Exception as exc:  # reduction must not blow up
            failures.append((label, vc_instance, "reduce raised %r" % (exc,)))
            return
        # Output must be a valid target instance.
        try:
            TARGET.validate(reduced)
        except InvalidInstance as exc:
            failures.append((label, vc_instance, "invalid target: %s" % exc))
            return
        got = solve_independent_set(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, vc_instance, "vc=%s is=%s reduced=%r"
                             % (expected, got, reduced)))

    # 1. Exhaustive: every graph on n = 0..4 vertices, every k in -2..n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
                check(inst, "exhaustive n=%d k=%d" % (n, k))

    # 2. Random graphs, n = 5..8, random k including out-of-range values.
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 8)
        edges = random_graph(n, rng.choice([0.0, 0.2, 0.5, 0.8, 1.0]), rng)
        k = rng.randint(-3, n + 3)
        inst = {"n": n, "edges": edges, "k": k}
        check(inst, "random n=%d k=%d" % (n, k))

    # 3. Explicit edge cases from the definitions.
    edge_cases = [
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": 3},
        {"n": 5, "edges": [], "k": -1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": -1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 0},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 99},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": -5},
    ]
    for inst in edge_cases:
        check(inst, "edge case")

    # 4. Reversed edge orientation must be handled the same.
    for _ in range(500):
        n = rng.randint(1, 7)
        edges = random_graph(n, 0.5, rng)
        flipped = [[v, u] for u, v in edges]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k}, "orientation A")
        check({"n": n, "edges": flipped, "k": k}, "orientation B")

    print("tests_run=%d tests_passed=%d" % (tests_run, tests_passed))
    if failures:
        print("FAILURES (%d):" % len(failures))
        for label, inst, msg in failures[:20]:
            print(" -", label, inst, msg)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = main()
    assert not failures, "reduction failed on %d cases" % len(failures)
    print("ALL TESTS PASSED")
