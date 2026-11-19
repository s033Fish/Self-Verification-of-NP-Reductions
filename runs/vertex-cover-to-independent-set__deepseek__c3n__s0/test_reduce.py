"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

import itertools

from problems import VertexCover, IndependentSet
from reduce import reduce
from solvers import vertex_cover_yes, independent_set_yes

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    VertexCover.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)  # reduction must produce a valid target
    src = vertex_cover_yes(instance)
    tgt = independent_set_yes(reduced)
    assert src == tgt, f"MISMATCH src={instance} -> {reduced}: {src} vs {tgt}"
    tests_passed += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive over all graphs with n = 0..4 and all k in -2..n+2
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Some larger random-ish structured cases
    import random
    random.seed(12345)
    for _ in range(300):
        n = random.randint(0, 7)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if random.random() < 0.4]
        k = random.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()


def test_edge_cases():
    # explicit edge cases from the docstrings
    cases = [
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": 5},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": -1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 0},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 3},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
    ]
    for c in cases:
        check(c)
    print(f"edge cases ok, tests_run={tests_run} tests_passed={tests_passed}")
