"""Tests for the Clique -> Independent Set reduction.

Contains brute-force solvers for both problems (written from the problem
definitions, since problems.py has no solvers) and compares the answers on
many small source instances with the answers on their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, straight from the definitions.

def _has_clique(n, edges, k):
    """Yes iff graph has a clique of at least k vertices."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if all(adj[a][b] for a, b in itertools.combinations(combo, 2)):
                return True
    return False


def _has_independent_set(n, edges, k):
    """Yes iff graph has an independent set of at least k vertices."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if not any(adj[a][b] for a, b in itertools.combinations(combo, 2)):
                return True
    return False


def solve_clique(instance):
    return _has_clique(instance["n"], instance["edges"], instance["k"])


def solve_independent_set(instance):
    return _has_independent_set(instance["n"], instance["edges"], instance["k"])


# ----------------------------------------------------------------------
# Instance generation.

def all_graphs(n):
    """All simple graphs on n labelled vertices (as edge lists)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [[u, v] for i, (u, v) in enumerate(pairs) if mask >> i & 1]


def random_instance(rng, max_n=6, max_k=7):
    n = rng.randint(0, max_n)
    pairs = list(itertools.combinations(range(n), 2))
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    k = rng.randint(-2, max_k)
    return {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Tests.

def test_exhaustive_small():
    """Exhaustive over all graphs with n <= 4 and all k in -2..n+2."""
    tests = 0
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                src = {"n": n, "edges": edges, "k": k}
                Clique.validate(src)
                tgt = reduce(src)
                IndependentSet.validate(tgt)
                a = solve_clique(src)
                b = solve_independent_set(tgt)
                assert a == b, (src, tgt, a, b)
                tests += 1
    return tests


def test_random_larger():
    rng = random.Random(12345)
    tests = 0
    for _ in range(3000):
        src = random_instance(rng, max_n=7, max_k=9)
        Clique.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        a = solve_clique(src)
        b = solve_independent_set(tgt)
        assert a == b, (src, tgt, a, b)
        tests += 1
    return tests


def test_structure():
    """The reduction must produce the complement graph and preserve n, k."""
    src = {"n": 5, "edges": [[0, 1], [2, 3], [0, 4]], "k": 2}
    tgt = reduce(src)
    assert tgt["n"] == 5 and tgt["k"] == 2
    expected = {
        frozenset(p)
        for p in itertools.combinations(range(5), 2)
        if frozenset(p) not in {frozenset(e) for e in src["edges"]}
    }
    got = {frozenset(e) for e in tgt["edges"]}
    assert got == expected, (got, expected)
    # edge count check
    assert len(tgt["edges"]) == 10 - 3
    return 1


def test_edge_cases():
    tests = 0
    # k <= 0 always yes
    for k in (-5, -1, 0):
        for n in range(0, 5):
            src = {"n": n, "edges": [], "k": k}
            assert solve_clique(src) is True
            assert solve_independent_set(reduce(src)) is True
            tests += 1
    # k > n always no
    for k in (3, 6):
        for n in range(0, 3):
            src = {"n": n, "edges": [], "k": k}
            assert solve_clique(src) is False
            assert solve_independent_set(reduce(src)) is False
            tests += 1
    # empty graph: clique of size 1 yes, independent set of size n yes
    src = {"n": 4, "edges": [], "k": 1}
    assert solve_clique(src) is True
    assert solve_independent_set(reduce(src)) is True
    tests += 1
    src = {"n": 4, "edges": [], "k": 4}
    assert solve_clique(src) is False  # no edges -> no 4-clique
    assert solve_independent_set(reduce(src)) is False
    tests += 1
    # complete graph: clique of size n yes, independent set of size 2 no
    complete = [[u, v] for u, v in itertools.combinations(range(4), 2)]
    src = {"n": 4, "edges": complete, "k": 4}
    assert solve_clique(src) is True
    assert solve_independent_set(reduce(src)) is True
    tests += 1
    src = {"n": 4, "edges": complete, "k": 2}
    assert solve_clique(src) is True
    assert solve_independent_set(reduce(src)) is True
    tests += 1
    # n = 0
    src = {"n": 0, "edges": [], "k": 0}
    assert solve_clique(src) is True
    assert solve_independent_set(reduce(src)) is True
    tests += 1
    src = {"n": 0, "edges": [], "k": 1}
    assert solve_clique(src) is False
    assert solve_independent_set(reduce(src)) is False
    tests += 1
    return tests


def main():
    total = 0
    passed = 0
    for name, fn in [
        ("test_exhaustive_small", test_exhaustive_small),
        ("test_random_larger", test_random_larger),
        ("test_structure", test_structure),
        ("test_edge_cases", test_edge_cases),
    ]:
        try:
            count = fn()
            total += count
            passed += count
            print(f"PASS {name}: {count} checks")
        except AssertionError as exc:
            total += 1
            print(f"FAIL {name}: {exc}")
            raise
    print(f"TOTAL: {passed}/{total} checks passed")
    return passed, total


if __name__ == "__main__":
    main()
