"""Tests comparing brute-force answers for Vertex Cover and the reduction."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import solve_dominating_set, solve_vertex_cover

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = solve_vertex_cover(instance)
    got = solve_dominating_set(reduced)
    if expected == got:
        tests_passed += 1
    else:
        raise AssertionError(
            f"mismatch: source={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive over all graphs with n <= 4 and a wide range of k.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": [list(e) for e in edges], "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 5)
        pairs = list(itertools.combinations(range(n), 2))
        rng.shuffle(pairs)
        m = rng.randint(0, len(pairs))
        edges = [list(e) for e in pairs[:m]]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 3, "edges": [], "k": 0})
    check({"n": 3, "edges": [], "k": -1})
    check({"n": 2, "edges": [[0, 1]], "k": 0})
    check({"n": 2, "edges": [[0, 1]], "k": 1})
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1})
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": -1})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
