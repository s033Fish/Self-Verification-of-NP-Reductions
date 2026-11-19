"""Tests for the Vertex Cover -> Set Cover reduction."""

from __future__ import annotations

import random

from problems import VertexCover, SetCover
from reduce import reduce
from solvers import vertex_cover_answer, set_cover_answer

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    VertexCover.validate(instance)
    reduced = reduce(instance)
    SetCover.validate(reduced)
    expected = vertex_cover_answer(instance)
    got = set_cover_answer(reduced)
    assert expected == got, (instance, reduced, expected, got)
    tests_passed += 1


def all_graphs(n):
    """All simple graphs on n labelled vertices."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for idx, p in enumerate(pairs) if mask >> idx & 1]
        yield edges


def main():
    # Exhaustive over all graphs up to n=4 and all relevant k values.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random small instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 7)
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        rng.shuffle(pairs)
        m = rng.randint(0, len(pairs))
        edges = [list(p) for p in pairs[:m]]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 3, "edges": [], "k": 0})
    check({"n": 3, "edges": [], "k": -1})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 0})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 2})
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1})
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3})
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2})

    # Check the shape of the reduction on a concrete instance.
    red = reduce({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1})
    assert red == {"universe_size": 2, "sets": [[0], [0, 1], [1]], "k": 1}, red

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
