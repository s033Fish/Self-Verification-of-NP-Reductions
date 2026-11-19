"""Independent checks for reduce.py: Independent Set -> Clique.

We implement our own brute-force solvers for both problems directly from the
docstrings in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


def _adjacency(instance):
    n = instance["n"]
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    return adj


def brute_independent_set(instance):
    """Yes iff there is an independent set of at least k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = _adjacency(instance)
    # Search all subsets of size exactly k (monotone: at least k == exists size k).
    for subset in itertools.combinations(range(n), k):
        ok = True
        for i in range(len(subset)):
            for j in range(i + 1, len(subset)):
                if adj[subset[i]][subset[j]]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


def brute_clique(instance):
    """Yes iff there is a clique of at least k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = _adjacency(instance)
    for subset in itertools.combinations(range(n), k):
        ok = True
        for i in range(len(subset)):
            for j in range(i + 1, len(subset)):
                if not adj[subset[i]][subset[j]]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


def solve_source(instance):
    IndependentSet.validate(instance)
    return brute_independent_set(instance)


def solve_target(instance):
    Clique.validate(instance)
    return brute_clique(instance)


def random_graph(n, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < rng.choice([0.0, 0.15, 0.3, 0.5, 0.7, 1.0]):
                edges.append([u, v])
    return edges


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            src = solve_source(instance)
            reduced = reduce(instance)
            # Reduction output must be a valid Clique instance.
            Clique.validate(reduced)
            tgt = solve_target(reduced)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, instance, f"exception: {exc!r}"))
            return
        if src != tgt:
            failures.append(
                (label, instance, f"source={src} target={tgt} reduced={reduced}")
            )
        else:
            tests_passed += 1

    # Exhaustive over all graphs for n = 0..4 and all k in a wide range.
    for n in range(0, 5):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, f"exhaustive n={n}")

    # Random graphs for n = 5..8, random k including edge cases.
    for _ in range(4000):
        n = rng.randint(0, 8)
        edges = random_graph(n, rng)
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k}, "random")

    # Explicit edge cases.
    explicit = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
    ]
    for inst in explicit:
        check(inst, "explicit")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, inst, msg in failures[:10]:
            print(label, inst, msg)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
