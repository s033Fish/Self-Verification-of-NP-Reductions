"""Tests for the Clique -> Vertex Cover reduction."""

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce
from solvers import clique_yes, vertex_cover_yes


def all_graphs(n):
    """All undirected simple graphs on n vertices (as edge lists)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def check(instance):
    Clique.validate(instance)
    reduced = reduce(instance)
    VertexCover.validate(reduced)
    a = clique_yes(instance)
    b = vertex_cover_yes(reduced)
    assert a == b, (instance, reduced, a, b)
    return a


def test_exhaustive_small():
    count = 0
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})
                count += 1
    return count


def test_random():
    rng = random.Random(12345)
    count = 0
    for _ in range(3000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})
        count += 1
    return count


def test_known_cases():
    # Triangle graph, k=3 -> clique yes; complement has no edges, k'=0 -> yes.
    inst = {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3}
    assert check(inst) is True
    # Empty graph on 3 vertices, k=2 -> no clique; complement complete, k'=1 -> no cover.
    inst = {"n": 3, "edges": [], "k": 2}
    assert check(inst) is False
    # k <= 0 always yes.
    assert check({"n": 4, "edges": [], "k": 0}) is True
    assert check({"n": 4, "edges": [], "k": -5}) is True
    # k > n always no.
    assert check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4}) is False
    # n = 0, k = 0 -> yes (empty clique).
    assert check({"n": 0, "edges": [], "k": 0}) is True
    # n = 0, k = 1 -> no.
    assert check({"n": 0, "edges": [], "k": 1}) is False
    return 6


if __name__ == "__main__":
    total = 0
    passed = 0
    for name, fn in [
        ("exhaustive_small", test_exhaustive_small),
        ("random", test_random),
        ("known_cases", test_known_cases),
    ]:
        try:
            c = fn()
            total += c
            passed += c
            print(f"PASS {name}: {c} checks")
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
            total += 1
    print(f"TOTAL checks={total} passed={passed}")
    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": passed == total, "tests_run": total, "tests_passed": passed}, f)
