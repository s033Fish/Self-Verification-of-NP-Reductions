"""Brute-force solvers and randomized/exhaustive tests for the reduction."""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


def _has_clique(n, edges, k):
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for subset in itertools.combinations(range(n), k):
        if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
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
    for subset in itertools.combinations(range(n), k):
        if not any(adj[a][b] for a, b in itertools.combinations(subset, 2)):
            return True
    return False


def solve_clique(instance):
    return _has_clique(instance["n"], instance["edges"], instance["k"])


def solve_independent_set(instance):
    return _has_independent_set(instance["n"], instance["edges"], instance["k"])


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [[u, v] for i, (u, v) in enumerate(pairs) if mask >> i & 1]


def test_exhaustive_small():
    tests = 0
    passed = 0
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-1, n + 3):
                src = {"n": n, "edges": edges, "k": k}
                Clique.validate(src)
                tgt = reduce(src)
                IndependentSet.validate(tgt)
                a = solve_clique(src)
                b = solve_independent_set(tgt)
                tests += 1
                if a == b:
                    passed += 1
                else:
                    raise AssertionError(
                        f"MISMATCH src={src} tgt={tgt} clique={a} iset={b}"
                    )
    return tests, passed


def test_random_medium():
    rng = random.Random(12345)
    tests = 0
    passed = 0
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < rng.random()]
        k = rng.randint(-2, n + 2)
        src = {"n": n, "edges": edges, "k": k}
        Clique.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        a = solve_clique(src)
        b = solve_independent_set(tgt)
        tests += 1
        if a == b:
            passed += 1
        else:
            raise AssertionError(
                f"MISMATCH src={src} tgt={tgt} clique={a} iset={b}"
            )
    return tests, passed


def test_edge_cases():
    tests = 0
    passed = 0
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 5, "edges": [], "k": -3},
        # complete graph K5
        {"n": 5, "edges": [[i, j] for i in range(5) for j in range(i + 1, 5)], "k": 5},
        {"n": 5, "edges": [[i, j] for i in range(5) for j in range(i + 1, 5)], "k": 4},
        # reversed edge orientation should behave identically
        {"n": 3, "edges": [[1, 0], [2, 1]], "k": 2},
    ]
    for src in cases:
        Clique.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        a = solve_clique(src)
        b = solve_independent_set(tgt)
        tests += 1
        if a == b:
            passed += 1
        else:
            raise AssertionError(f"MISMATCH src={src} tgt={tgt} clique={a} iset={b}")
    return tests, passed


def main():
    total_tests = 0
    total_passed = 0
    for fn in (test_exhaustive_small, test_random_medium, test_edge_cases):
        t, p = fn()
        print(f"{fn.__name__}: {p}/{t} passed")
        total_tests += t
        total_passed += p
    print(f"TOTAL: {total_passed}/{total_tests} passed")
    assert total_passed == total_tests
    return total_tests, total_passed


if __name__ == "__main__":
    main()
