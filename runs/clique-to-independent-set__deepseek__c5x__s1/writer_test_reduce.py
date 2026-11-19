"""Tests for the Clique -> Independent Set reduction."""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def _has_clique(n, edges, k):
    if k <= 0:
        return True
    if k > n:
        return False
    edge_set = {frozenset(e) for e in edges}
    for combo in itertools.combinations(range(n), k):
        if all(frozenset(p) in edge_set for p in itertools.combinations(combo, 2)):
            return True
    return False


def _has_independent_set(n, edges, k):
    if k <= 0:
        return True
    if k > n:
        return False
    edge_set = {frozenset(e) for e in edges}
    for combo in itertools.combinations(range(n), k):
        if all(frozenset(p) not in edge_set for p in itertools.combinations(combo, 2)):
            return True
    return False


def solve_clique(instance):
    return _has_clique(instance["n"], instance["edges"], instance["k"])


def solve_independent_set(instance):
    return _has_independent_set(instance["n"], instance["edges"], instance["k"])


# ----------------------------------------------------------------------
# Instance generation.

def random_instance(rng, max_n=7):
    n = rng.randint(0, max_n)
    all_pairs = list(itertools.combinations(range(n), 2))
    edges = [list(p) for p in all_pairs if rng.random() < 0.5]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def all_instances(max_n=5):
    """Exhaustively enumerate small graphs and a range of k values."""
    for n in range(0, max_n + 1):
        all_pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-1, n + 2):
                yield {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive small cases.
    for inst in all_instances(max_n=5):
        Clique.validate(inst)
        out = reduce(inst)
        IndependentSet.validate(out)
        expected = solve_clique(inst)
        got = solve_independent_set(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", inst, "->", out, "expected", expected, "got", got)

    # Random larger cases.
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_instance(rng, max_n=8)
        Clique.validate(inst)
        out = reduce(inst)
        IndependentSet.validate(out)
        expected = solve_clique(inst)
        got = solve_independent_set(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", inst, "->", out, "expected", expected, "got", got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
