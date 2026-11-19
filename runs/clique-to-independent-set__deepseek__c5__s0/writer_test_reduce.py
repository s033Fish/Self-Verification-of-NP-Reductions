"""Tests comparing brute-force answers on Clique instances and their reductions."""

from __future__ import annotations

import itertools

from problems import Clique, IndependentSet
from reduce import reduce
from solvers import solve_clique, solve_independent_set

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    Clique.validate(instance)
    out = reduce(instance)
    IndependentSet.validate(out)
    src = solve_clique(instance)
    tgt = solve_independent_set(out)
    assert src == tgt, f"mismatch: {instance} -> {out}, src={src}, tgt={tgt}"
    tests_passed += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive over all graphs for n = 0..5 and all relevant k.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # A few larger random-ish structured cases.
    import random
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-1, n + 2)
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
