"""Tests for the Clique -> Independent Set reduction.

Includes brute-force solvers for both problems (from the definitions in
problems.py) and compares answers on many small random instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


def brute_clique(instance) -> bool:
    """Yes iff the graph has a clique of at least k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def brute_independent_set(instance) -> bool:
    """Yes iff the graph has an independent set of at least k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if not any(adj[a][b] for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def random_instance(rng: random.Random, max_n: int = 7) -> dict:
    n = rng.randint(0, max_n)
    all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(p) for p in all_pairs if rng.random() < 0.5]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    # 1) Randomized instances.
    for _ in range(4000):
        inst = random_instance(rng)
        Clique.validate(inst)
        red = reduce(inst)
        IndependentSet.validate(red)

        expected = brute_clique(inst)
        got = brute_independent_set(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, red, expected, got))

    # 2) Exhaustive over all graphs with n <= 4 and k in -1..n+1.
    for n in range(0, 5):
        all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_pairs)):
            edges = [list(p) for i, p in enumerate(all_pairs) if mask >> i & 1]
            for k in range(-1, n + 2):
                inst = {"n": n, "edges": edges, "k": k}
                Clique.validate(inst)
                red = reduce(inst)
                IndependentSet.validate(red)
                expected = brute_clique(inst)
                got = brute_independent_set(red)
                tests_run += 1
                if expected == got:
                    tests_passed += 1
                else:
                    failures.append((inst, red, expected, got))

    # 3) Explicit edge cases.
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
    ]
    for inst in cases:
        Clique.validate(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        expected = brute_clique(inst)
        got = brute_independent_set(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, red, expected, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
