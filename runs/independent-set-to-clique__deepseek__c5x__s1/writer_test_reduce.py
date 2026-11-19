"""Tests comparing brute-force answers on source instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, Clique
from reduce import reduce
from solvers import independent_set_solver, clique_solver

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    IndependentSet.validate(instance)
    out = reduce(instance)
    Clique.validate(out)
    src = independent_set_solver(instance)
    tgt = clique_solver(out)
    assert src == tgt, (instance, out, src, tgt)
    tests_passed += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if mask >> i & 1]


def main():
    # Exhaustive small graphs, all k values including edge cases.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        edges = []
        for u, v in itertools.combinations(range(n), 2):
            if rng.random() < 0.5:
                edges.append([u, v])
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
