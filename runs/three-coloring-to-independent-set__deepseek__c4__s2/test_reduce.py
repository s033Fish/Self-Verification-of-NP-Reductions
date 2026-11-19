"""Brute-force solvers and tests for the 3-Coloring -> Independent Set reduction."""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeColoring, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_three_coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    for colors in itertools.product(range(3), repeat=n):
        if all(colors[u] != colors[v] for u, v in edges):
            return True
    return False


def solve_independent_set(instance):
    """Brute force: search for an independent set of size >= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u

    # Recursive search over vertices, tracking best independent set size.
    best = 0

    def rec(i, chosen_mask, count):
        nonlocal best
        if count > best:
            best = count
        if best >= k:
            return
        if i == n:
            return
        # upper bound: remaining vertices
        if count + (n - i) <= best:
            return
        # branch: include i if possible
        if not (adj[i] & chosen_mask):
            rec(i + 1, chosen_mask | (1 << i), count + 1)
        rec(i + 1, chosen_mask, count)

    rec(0, 0, 0)
    return best >= k


# ----------------------------------------------------------------------
# Helpers to build random valid instances.

def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def all_graphs(n):
    """All labeled graphs on n vertices (each possible edge in or out)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0

    def check(source_instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Validate both instances against the official validators.
        ThreeColoring.validate(source_instance)
        target = reduce(source_instance)
        IndependentSet.validate(target)
        expected = solve_three_coloring(source_instance)
        got = solve_independent_set(target)
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", source_instance, "expected", expected, "got", got)
            raise AssertionError("reduction mismatch")

    # Exhaustive over all graphs on 0..5 vertices (1 + 1 + 2 + 8 + 64 + 1024).
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random graphs on up to 8 vertices.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 8)
        p = rng.choice([0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0])
        check(random_graph(n, p, rng))

    # Specific edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    # K4 is not 3-colourable.
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})
    # K5 is not 3-colourable.
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]})
    # Empty graph on many vertices is 3-colourable.
    check({"n": 12, "edges": []})
    # Odd cycle of length 5 is 3-colourable.
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)


if __name__ == "__main__":
    main()
