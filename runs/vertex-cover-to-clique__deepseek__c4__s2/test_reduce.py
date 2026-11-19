"""Tests comparing brute-force answers on source instances and reductions."""

import itertools
import random

from problems import VertexCover, Clique
from solvers import vertex_cover_yes, clique_yes
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    VertexCover.validate(instance)
    out = reduce(instance)
    Clique.validate(out)
    expected = vertex_cover_yes(instance)
    got = clique_yes(out)
    assert expected == got, (instance, out, expected, got)
    tests_passed += 1


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive over all graphs on 0..4 vertices and a range of k values.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": [list(e) for e in edges], "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(pairs)
        m = rng.randint(0, len(pairs))
        edges = [list(p) for p in pairs[:m]]
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 0, "edges": [], "k": 5})
    check({"n": 3, "edges": [], "k": 0})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3})
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1})
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
