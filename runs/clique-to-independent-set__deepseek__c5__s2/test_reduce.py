"""Independent tests for reduce.py: Clique -> Independent Set.

We write our own brute-force solvers from the problem definitions, then
compare solver answers on many small source instances against the answers
on their reductions.
"""
from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the definitions.
# ----------------------------------------------------------------------

def _has_clique(n, edges, k):
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for combo in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(combo, 2)):
            return True
    return False


def _has_independent_set(n, edges, k):
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for combo in itertools.combinations(range(n), k):
        if not any(adj[u][v] for u, v in itertools.combinations(combo, 2)):
            return True
    return False


def solve_clique(instance):
    return _has_clique(instance["n"], instance["edges"], instance["k"])


def solve_independent_set(instance):
    return _has_independent_set(instance["n"], instance["edges"], instance["k"])


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_instance(rng, max_n=7, k_range=(-2, 9)):
    n = rng.randint(0, max_n)
    all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(e) for e in all_pairs if rng.random() < 0.5]
    rng.shuffle(edges)
    # randomly reverse some edges to test undirected handling
    for e in edges:
        if rng.random() < 0.5:
            e.reverse()
    k = rng.randint(*k_range)
    return {"n": n, "edges": edges, "k": k}


def exhaustive_instances(max_n=5):
    """All graphs on 0..max_n vertices with all k in a wide range."""
    for n in range(max_n + 1):
        all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-2, n + 3):
                yield {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # validate input instance
        Clique.validate(instance)
        expected = solve_clique(instance)
        reduced = reduce(instance)
        # reduced instance must be a valid IndependentSet instance
        IndependentSet.validate(reduced)
        got = solve_independent_set(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, instance, reduced, expected, got))

    # 1. Exhaustive small instances
    for inst in exhaustive_instances(max_n=5):
        check(inst, "exhaustive")

    # 2. Random instances
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng), "random")

    # 3. Explicit edge cases
    explicit = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 5, "edges": [], "k": 1},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]], "k": 3},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [0, 3], [0, 2], [1, 3]], "k": 4},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [0, 3], [0, 2], [1, 3]], "k": 5},
        {"n": 3, "edges": [[0, 1]], "k": -1},
        {"n": 3, "edges": [[0, 1]], "k": 0},
    ]
    for inst in explicit:
        check(inst, "explicit")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for label, inst, reduced, expected, got in failures[:10]:
        print("FAIL", label, inst, "->", reduced, "expected", expected, "got", got)

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tr, tp, fails = main()
    assert not fails, "reduction failed on some instances"
    print("ALL TESTS PASSED")
