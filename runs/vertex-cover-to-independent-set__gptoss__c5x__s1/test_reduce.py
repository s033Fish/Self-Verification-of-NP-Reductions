"""Independent verification of reduce.py: Vertex Cover -> Independent Set.

We implement brute-force solvers for both problems directly from the
docstring definitions in problems.py, then compare answers on many small
source instances against the answers of their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def vertex_cover_yes(instance) -> bool:
    """True iff graph has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    # try all subsets of size <= k
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def independent_set_yes(instance) -> bool:
    """True iff graph has an independent set of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # try all subsets of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(not (u in chosen and v in chosen) for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def random_graph_instance(rng, max_n=6, max_k_extra=2):
    n = rng.randint(0, max_n)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [[u, v] for (u, v) in all_edges[:m]]
    k = rng.randint(-2, n + max_k_extra)
    return {"n": n, "edges": edges, "k": k}


def all_instances(max_n=4):
    """Exhaustively generate all small instances (all graphs, all k)."""
    for n in range(0, max_n + 1):
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_edges)):
            edges = [[u, v] for i, (u, v) in enumerate(all_edges) if mask >> i & 1]
            for k in range(-2, n + 3):
                yield {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # validate source
        VertexCover.validate(inst)
        expected = vertex_cover_yes(inst)
        red = reduce(inst)
        # reduction output must be a valid target instance
        IndependentSet.validate(red)
        got = independent_set_yes(red)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, red, expected, got))

    # Exhaustive small instances
    for inst in all_instances(max_n=4):
        check(inst)

    # Random larger instances
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_graph_instance(rng, max_n=7, max_k_extra=3))

    # Targeted edge cases
    targeted = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 5},
        {"n": 1, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 100},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 0},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 4},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 5},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": -1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 0]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 0]], "k": 2},
    ]
    for inst in targeted:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for inst, red, expected, got in failures[:10]:
            print("  inst=", inst, "red=", red, "expected=", expected, "got=", got)
        raise SystemExit(1)
    print("ALL PASSED")

    return tests_run, tests_passed


if __name__ == "__main__":
    main()
