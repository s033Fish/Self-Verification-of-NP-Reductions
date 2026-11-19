"""Tests for the Vertex Cover -> Independent Set reduction.

We brute-force both problems on many small instances and check that
    solve_vertex_cover(I) == solve_independent_set(reduce(I)).
We also validate that reduce returns a well-formed Independent Set instance
and that reduce does not mutate/alias the input.
"""

from __future__ import annotations

import itertools

from problems import VertexCover, IndependentSet
from reduce import reduce
from solvers import solve_vertex_cover, solve_independent_set


def all_graphs(n):
    """All simple undirected graphs on n vertices (as edge lists)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    # Exhaustive: all graphs on 0..4 vertices, all k in -2..n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                instance = {"n": n, "edges": [list(e) for e in edges], "k": k}
                VertexCover.validate(instance)
                out = reduce(instance)
                IndependentSet.validate(out)

                src = solve_vertex_cover(instance)
                tgt = solve_independent_set(out)
                tests_run += 1
                if src == tgt:
                    tests_passed += 1
                else:
                    failures.append((instance, out, src, tgt))

                # input must not be mutated and output must not alias input
                if instance["k"] != k or out["edges"] is instance["edges"]:
                    failures.append(("mutation/alias", instance, out))

    # A few random larger sparse graphs (n up to 8) to be safe.
    import random
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.35]
        k = rng.randint(-2, n + 2)
        instance = {"n": n, "edges": edges, "k": k}
        VertexCover.validate(instance)
        out = reduce(instance)
        IndependentSet.validate(out)
        src = solve_vertex_cover(instance)
        tgt = solve_independent_set(out)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((instance, out, src, tgt))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES (first 5):")
        for f in failures[:5]:
            print(f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
