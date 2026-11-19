"""Tests for the Independent Set -> Vertex Cover reduction.

Contains brute-force solvers for both problems (written from the
definitions in problems.py, which provides no solvers) and checks that
reduce() preserves the answer on many small instances, including all the
documented edge cases.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (definition-based)


def _is_independent(n, edges, chosen):
    chosen = set(chosen)
    return all(not (u in chosen and v in chosen) for u, v in edges)


def solve_independent_set(instance):
    """Yes iff there is an independent set of at least k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if _is_independent(n, edges, subset):
                return True
    return False


def _is_vertex_cover(edges, chosen):
    chosen = set(chosen)
    return all(u in chosen or v in chosen for u, v in edges)


def solve_vertex_cover(instance):
    """Yes iff there is a vertex cover of at most k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            if _is_vertex_cover(edges, subset):
                return True
    return False


# ----------------------------------------------------------------------
# Helpers


def make_instance(n, edges, k):
    return {"n": n, "edges": [list(e) for e in edges], "k": k}


def random_graph(rng, n, p=0.4):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


# ----------------------------------------------------------------------
# Tests


def test_solvers_agree_on_trivial_cases():
    # k <= 0 always independent-set yes; k > n always no.
    assert solve_independent_set(make_instance(3, [[0, 1]], 0)) is True
    assert solve_independent_set(make_instance(3, [[0, 1]], -5)) is True
    assert solve_independent_set(make_instance(3, [[0, 1]], 4)) is False
    # k < 0 vertex cover no; k >= n vertex cover yes.
    assert solve_vertex_cover(make_instance(3, [[0, 1]], -1)) is False
    assert solve_vertex_cover(make_instance(3, [[0, 1]], 3)) is True
    # no edges: independent set yes for k <= n; vertex cover yes for k >= 0.
    assert solve_independent_set(make_instance(4, [], 4)) is True
    assert solve_independent_set(make_instance(4, [], 5)) is False
    assert solve_vertex_cover(make_instance(4, [], 0)) is True
    assert solve_vertex_cover(make_instance(4, [], -1)) is False


def test_known_examples():
    # Path 0-1-2: max independent set size 2, min vertex cover size 1.
    assert solve_independent_set(make_instance(3, [[0, 1], [1, 2]], 2)) is True
    assert solve_independent_set(make_instance(3, [[0, 1], [1, 2]], 3)) is False
    assert solve_vertex_cover(make_instance(3, [[0, 1], [1, 2]], 1)) is True
    assert solve_vertex_cover(make_instance(3, [[0, 1], [1, 2]], 0)) is False
    # Triangle: max independent set 1, min vertex cover 2.
    tri = [[0, 1], [1, 2], [0, 2]]
    assert solve_independent_set(make_instance(3, tri, 2)) is False
    assert solve_vertex_cover(make_instance(3, tri, 1)) is False
    assert solve_vertex_cover(make_instance(3, tri, 2)) is True


def test_reduction_preserves_answer_exhaustive_small():
    """Exhaustively check all graphs on n <= 4 and a range of k."""
    tests_run = 0
    for n in range(0, 5):
        all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                inst = make_instance(n, edges, k)
                IndependentSet.validate(inst)
                out = reduce(inst)
                VertexCover.validate(out)
                src = solve_independent_set(inst)
                tgt = solve_vertex_cover(out)
                assert src == tgt, (inst, out, src, tgt)
                tests_run += 1
    return tests_run


def test_reduction_preserves_answer_random():
    rng = random.Random(12345)
    tests_run = 0
    for _ in range(400):
        n = rng.randint(0, 9)
        edges = random_graph(rng, n, p=rng.choice([0.0, 0.2, 0.5, 0.9, 1.0]))
        k = rng.randint(-3, n + 3)
        inst = make_instance(n, edges, k)
        IndependentSet.validate(inst)
        out = reduce(inst)
        VertexCover.validate(out)
        assert solve_independent_set(inst) == solve_vertex_cover(out), (inst, out)
        tests_run += 1
    return tests_run


def test_reduction_shape_and_polynomial():
    inst = make_instance(5, [[0, 1], [3, 4]], 2)
    out = reduce(inst)
    assert out == {"n": 5, "edges": [[0, 1], [3, 4]], "k": 3}
    # n and edges are unchanged; only k is transformed.
    assert out["n"] == inst["n"]
    assert out["edges"] == inst["edges"]
    assert out["k"] == inst["n"] - inst["k"]


def main():
    tests = [
        ("solvers_trivial", test_solvers_agree_on_trivial_cases),
        ("known_examples", test_known_examples),
        ("reduction_exhaustive_small", test_reduction_preserves_answer_exhaustive_small),
        ("reduction_random", test_reduction_preserves_answer_random),
        ("reduction_shape", test_reduction_shape_and_polynomial),
    ]
    passed = 0
    total = 0
    for name, fn in tests:
        result = fn()
        # Each test counts as one "test"; exhaustive/random report inner counts.
        total += 1
        passed += 1
        print(f"PASS {name}" + (f" ({result} comparisons)" if isinstance(result, int) else ""))
    print(f"\n{passed}/{total} test functions passed")
    return passed, total


if __name__ == "__main__":
    main()
