"""Tests for the Independent Set -> Clique reduction.

problems.py has no solvers, so we implement brute-force solvers from the
definitions, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (definition-based)

def _has_independent_set(n, edges, k):
    if k <= 0:
        return True
    if k > n:
        return False
    edge_set = {frozenset(e) for e in edges}
    for subset in itertools.combinations(range(n), k):
        s = set(subset)
        ok = True
        for u, v in itertools.combinations(subset, 2):
            if frozenset((u, v)) in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def _has_clique(n, edges, k):
    if k <= 0:
        return True
    if k > n:
        return False
    edge_set = {frozenset(e) for e in edges}
    for subset in itertools.combinations(range(n), k):
        ok = True
        for u, v in itertools.combinations(subset, 2):
            if frozenset((u, v)) not in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance):
    return _has_independent_set(instance["n"], instance["edges"], instance["k"])


def solve_clique(instance):
    return _has_clique(instance["n"], instance["edges"], instance["k"])


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    # validate both sides
    IndependentSet.validate(instance)
    reduced = reduce(instance)
    Clique.validate(reduced)
    expected = solve_independent_set(instance)
    got = solve_clique(reduced)
    if expected == got:
        tests_passed += 1
    else:
        raise AssertionError(
            f"MISMATCH: {instance} -> {reduced}, expected {expected}, got {got}"
        )


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]
        yield edges


def main():
    # Exhaustive: all graphs on n = 0..5, all k in -2..n+2.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(2000):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -5})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 2})
    check({"n": 4, "edges": [], "k": 4})            # no edges -> IS yes
    check({"n": 4, "edges": [], "k": 5})            # k > n -> no
    complete4 = [[u, v] for u, v in itertools.combinations(range(4), 2)]
    check({"n": 4, "edges": complete4, "k": 2})     # complete -> IS size 1
    check({"n": 4, "edges": complete4, "k": 1})     # IS size 1 yes
    check({"n": 4, "edges": complete4, "k": 0})     # k<=0 yes

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)


if __name__ == "__main__":
    main()
