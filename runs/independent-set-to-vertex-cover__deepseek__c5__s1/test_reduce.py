"""Independent verification of reduce.py: Independent Set -> Vertex Cover.

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, then compare answers on many small source
instances against the answers of their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the problem definitions.

def solve_independent_set(instance) -> bool:
    """Yes iff there is an independent set of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edge_set = {frozenset(e) for e in edges}
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(not (frozenset(e) <= s) for e in edge_set):
                return True
    return False


def solve_vertex_cover(instance) -> bool:
    """Yes iff there is a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(e[0] in s or e[1] in s for e in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation: all graphs on n vertices, all k in a range.

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    # Exhaustive: every graph on n = 0..5 vertices, k in [-2, n+2].
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
                IndependentSet.validate(inst)
                out = reduce(inst)
                VertexCover.validate(out)
                expected = solve_independent_set(inst)
                got = solve_vertex_cover(out)
                tests_run += 1
                if expected == got:
                    tests_passed += 1
                else:
                    failures.append((inst, out, expected, got))

    # Randomized larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.4]
        k = rng.randint(-3, n + 3)
        inst = {"n": n, "edges": edges, "k": k}
        IndependentSet.validate(inst)
        out = reduce(inst)
        VertexCover.validate(out)
        expected = solve_independent_set(inst)
        got = solve_vertex_cover(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, out, expected, got))

    # Structural checks: same graph, k mapped to n-k.
    for _ in range(500):
        n = rng.randint(0, 8)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-3, n + 3)
        inst = {"n": n, "edges": edges, "k": k}
        out = reduce(inst)
        tests_run += 1
        ok = (
            out["n"] == n
            and {frozenset(e) for e in out["edges"]} == {frozenset(e) for e in edges}
            and out["k"] == n - k
        )
        if ok:
            tests_passed += 1
        else:
            failures.append((inst, out, "structure", None))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES (first 5):")
        for f in failures[:5]:
            print(f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()
