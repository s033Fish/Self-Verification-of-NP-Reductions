"""Tests for reduce.py: brute-force solvers + randomized comparison."""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


def brute_clique(instance):
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def brute_independent_set(instance):
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if not any(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def random_instance(rng, max_n=7):
    n = rng.randint(0, max_n)
    all_pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(all_pairs)
    m = rng.randint(0, len(all_pairs))
    edges = [list(e) for e in all_pairs[:m]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0
    rng = random.Random(12345)

    # Deterministic edge cases.
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": -1},
    ]

    for inst in cases:
        tests_run += 1
        Clique.validate(inst)
        out = reduce(inst)
        IndependentSet.validate(out)
        a = brute_clique(inst)
        b = brute_independent_set(out)
        assert a == b, (inst, out, a, b)
        tests_passed += 1

    # Randomized comparison.
    for _ in range(3000):
        inst = random_instance(rng)
        tests_run += 1
        Clique.validate(inst)
        out = reduce(inst)
        IndependentSet.validate(out)
        a = brute_clique(inst)
        b = brute_independent_set(out)
        assert a == b, (inst, out, a, b)
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
