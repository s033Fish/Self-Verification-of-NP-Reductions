"""Tests for reduce.py: compare brute-force answers on source instances
and their reductions, across many small random/exhaustive instances."""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, Clique
from reduce import reduce
from solvers import solve_independent_set, solve_clique

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    IndependentSet.validate(instance)
    out = reduce(instance)
    Clique.validate(out)
    src = solve_independent_set(instance)
    tgt = solve_clique(out)
    assert src == tgt, (
        f"mismatch: instance={instance} reduced={out} "
        f"source_answer={src} target_answer={tgt}"
    )
    tests_passed += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield edges


def main():
    # Exhaustive: all graphs on n=0..4 vertices, all k in -1..n+1.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-1, n + 2):
                check({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Edge cases explicitly.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 5, "edges": [], "k": 5})
    check({"n": 5, "edges": [], "k": 6})
    check({"n": 5, "edges": [], "k": -3})
    # complete graph
    complete = [[u, v] for u, v in itertools.combinations(range(5), 2)]
    check({"n": 5, "edges": complete, "k": 1})
    check({"n": 5, "edges": complete, "k": 2})
    # reversed edge order should be fine
    check({"n": 3, "edges": [[2, 1]], "k": 2})
    check({"n": 3, "edges": [[2, 1]], "k": 3})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
