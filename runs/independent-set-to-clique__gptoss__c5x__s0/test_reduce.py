"""Independent tests for reduce.py (Independent Set -> Clique).

We implement brute-force solvers directly from the problem definitions in
problems.py and compare SOURCE answers with TARGET answers on the reduction.
"""

from __future__ import annotations

import itertools
import random

from problems import IndependentSet, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the definitions.
# ----------------------------------------------------------------------

def _edge_set(instance):
    return {frozenset(e) for e in instance["edges"]}


def solve_independent_set(instance):
    """Yes iff graph has an independent set of at least k vertices."""
    IndependentSet.validate(instance)
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edges = _edge_set(instance)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(frozenset((u, v)) not in edges
                   for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def solve_clique(instance):
    """Yes iff graph has a clique of at least k vertices."""
    Clique.validate(instance)
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edges = _edge_set(instance)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(frozenset((u, v)) in edges
                   for u, v in itertools.combinations(subset, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    """Yield every simple graph on n labelled vertices as an edge list."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield edges


def make_instance(n, edges, k):
    return {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label):
    global tests_run, tests_passed
    tests_run += 1
    src = solve_independent_set(instance)
    reduced = reduce(instance)
    # The reduction must produce a valid Clique instance.
    try:
        Clique.validate(reduced)
    except Exception as exc:  # noqa: BLE001
        failures.append((label, instance, reduced, f"invalid target: {exc!r}"))
        return
    tgt = solve_clique(reduced)
    if src == tgt:
        tests_passed += 1
    else:
        failures.append((label, instance, reduced, (src, tgt)))


def main():
    # 1. Exhaustive over all graphs on n = 0..5, all k in a wide range.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check(make_instance(n, edges, k), f"exhaustive n={n}")

    # 2. Exhaustive over all graphs on n = 6 with a few k values.
    for edges in all_graphs(6):
        for k in (-1, 0, 1, 2, 3, 4, 6, 7):
            check(make_instance(6, edges, k), "exhaustive n=6")

    # 3. Random larger instances.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 12)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < rng.choice([0.0, 0.15, 0.5, 0.85, 1.0])]
        k = rng.randint(-3, n + 3)
        check(make_instance(n, edges, k), "random")

    # 4. Targeted edge cases.
    check(make_instance(0, [], 0), "n=0 k=0")
    check(make_instance(0, [], 1), "n=0 k=1")
    check(make_instance(0, [], -5), "n=0 k<0")
    check(make_instance(5, [], 5), "empty graph independent set all")
    check(make_instance(5, [], 6), "empty graph k>n")
    complete5 = [list(p) for p in itertools.combinations(range(5), 2)]
    check(make_instance(5, complete5, 2), "complete graph IS k=2")
    check(make_instance(5, complete5, 1), "complete graph IS k=1")
    check(make_instance(1, [], 1), "single vertex IS")
    check(make_instance(1, [], 2), "single vertex k>n")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAIL:", f)
    return failures


if __name__ == "__main__":
    fails = main()
    raise SystemExit(1 if fails else 0)
