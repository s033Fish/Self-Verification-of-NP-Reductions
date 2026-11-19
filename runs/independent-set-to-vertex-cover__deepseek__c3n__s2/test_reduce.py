"""Tests for reduce.py: Independent Set -> Vertex Cover.

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, then check that for many small instances the
answer to the source instance equals the answer to its reduction.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def is_independent_set(n, edges, chosen):
    chosen = set(chosen)
    for u, v in edges:
        if u in chosen and v in chosen:
            return False
    return True


def solve_independent_set(instance):
    """Yes iff there is an independent set of size >= k."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if is_independent_set(n, edges, combo):
                return True
    return False


def is_vertex_cover(n, edges, chosen):
    chosen = set(chosen)
    for u, v in edges:
        if u not in chosen and v not in chosen:
            return False
    return True


def solve_vertex_cover(instance):
    """Yes iff there is a vertex cover of size <= k."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            if is_vertex_cover(n, edges, combo):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def random_instance(rng, n_max=6):
    n = rng.randint(0, n_max)
    all_pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(all_pairs)
    m = rng.randint(0, len(all_pairs))
    edges = [list(p) for p in all_pairs[:m]]
    # sometimes flip orientation
    for e in edges:
        if rng.random() < 0.5:
            e.reverse()
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def all_instances(n_max=5):
    """Exhaustive over all graphs up to n_max and a range of k."""
    for n in range(0, n_max + 1):
        all_pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                yield {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # validate both instances against the real problem definitions
        IndependentSet.validate(inst)
        red = reduce(inst)
        VertexCover.validate(red)
        src_ans = solve_independent_set(inst)
        tgt_ans = solve_vertex_cover(red)
        if src_ans != tgt_ans:
            raise AssertionError(
                f"MISMATCH: source={inst} ans={src_ans}, "
                f"reduced={red} ans={tgt_ans}"
            )
        # also check the reduction is exactly the complement mapping
        assert red["n"] == inst["n"]
        assert red["k"] == inst["n"] - inst["k"]
        assert sorted(map(tuple, red["edges"])) == sorted(map(tuple, inst["edges"]))
        tests_passed += 1

    # 1) Exhaustive small cases
    for inst in all_instances(n_max=5):
        check(inst)

    # 2) Random cases, slightly larger
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng, n_max=8))

    # 3) Explicit edge cases
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 0, "edges": [], "k": -3},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 5, "edges": [], "k": -1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 3},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
    ]
    for inst in edge_cases:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
