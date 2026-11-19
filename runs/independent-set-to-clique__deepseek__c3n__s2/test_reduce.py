"""Tests for the Independent Set -> Clique reduction."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce
from solvers import solve_clique, solve_independent_set

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    problems.IndependentSet.validate(instance)
    out = reduce(instance)
    problems.Clique.validate(out)  # reduction must produce a valid target instance
    expected = solve_independent_set(instance)
    got = solve_clique(out)
    assert got == expected, (instance, out, expected, got)
    TESTS_PASSED += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def test_exhaustive_small():
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})


def test_edge_cases():
    # k <= 0 always yes; k > n always no; no edges -> everything independent.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -5})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 3, "edges": [], "k": 3})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})
    check({"n": 1, "edges": [], "k": 1})


def test_random():
    rng = random.Random(12345)
    for _ in range(2000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        rng.shuffle(pairs)
        m = rng.randint(0, len(pairs))
        edges = [list(p) for p in pairs[:m]]
        k = rng.randint(-1, n + 2)
        check({"n": n, "edges": edges, "k": k})


if __name__ == "__main__":
    test_edge_cases()
    test_exhaustive_small()
    test_random()
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED
    print("ALL TESTS PASSED")
