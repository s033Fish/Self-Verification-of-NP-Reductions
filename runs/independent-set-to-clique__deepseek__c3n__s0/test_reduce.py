"""Tests comparing brute-force answers on source instances and reductions."""

from __future__ import annotations

from itertools import combinations

from problems import IndependentSet, Clique
from reduce import reduce
from solvers import solve_independent_set, solve_clique

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    IndependentSet.validate(instance)
    reduced = reduce(instance)
    Clique.validate(reduced)
    src = solve_independent_set(instance)
    tgt = solve_clique(reduced)
    assert src == tgt, (instance, reduced, src, tgt)
    tests_passed += 1


def all_graphs(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive over all graphs on n <= 5 vertices, all relevant k.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 1})
    check({"n": 3, "edges": [], "k": 3})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 3})
    check({"n": 5, "edges": [[0, 1], [2, 3]], "k": 3})
    check({"n": 5, "edges": [[0, 1], [2, 3]], "k": 4})
    check({"n": 6, "edges": [[0, 1], [1, 2], [3, 4], [4, 5]], "k": 3})

    # Random-ish larger instances.
    import random
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 12)
        pairs = list(combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-1, n + 1)
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
