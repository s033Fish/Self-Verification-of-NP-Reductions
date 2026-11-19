"""Compare brute-force answers on many small source instances and reductions."""

from __future__ import annotations

import random

from problems import Clique, IndependentSet
from reduce import reduce
from solvers import solve_clique, solve_independent_set

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    Clique.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)
    expected = solve_clique(instance)
    got = solve_independent_set(reduced)
    assert expected == got, (instance, reduced, expected, got)
    TESTS_PASSED += 1


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive over all graphs for n = 0..4 and all relevant k.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.5:
                    edges.append([u, v])
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -5})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 1})
    check({"n": 3, "edges": [], "k": 3})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
