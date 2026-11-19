"""Independent verification of reduce.py (Clique -> Independent Set).

We write brute-force solvers for both problems from the definitions in
problems.py, then compare the solver answer on many small Clique instances
with the solver answer on their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstring definitions)

def _has_clique(n, edges, k):
    """True iff graph has a clique of AT LEAST k vertices."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if not adj[a][b]:
                    ok = False
                    break
            if ok:
                return True
    return False


def _has_independent_set(n, edges, k):
    """True iff graph has an independent set of AT LEAST k vertices."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if adj[a][b]:
                    ok = False
                    break
            if ok:
                return True
    return False


def solve_clique(instance):
    return _has_clique(instance["n"], instance["edges"], instance["k"])


def solve_independent_set(instance):
    return _has_independent_set(instance["n"], instance["edges"], instance["k"])


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    """Yield every simple graph on n vertices as a list of edges."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]


def random_graph(n, rng):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    return [list(p) for p in pairs if rng.random() < 0.5]


# ----------------------------------------------------------------------
# Tests

def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # The input must be a valid Clique instance.
        Clique.validate(instance)
        reduced = reduce(instance)
        # The reduction must produce a valid Independent Set instance.
        IndependentSet.validate(reduced)
        expected = solve_clique(instance)
        got = solve_independent_set(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((instance, reduced, expected, got))

    # 1. Exhaustive over all graphs for n = 0..4, and all relevant k.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # 2. Random larger instances (n up to 8), random k including edges cases.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        edges = random_graph(n, rng)
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # 3. Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 0, "edges": [], "k": -5})
    check({"n": 1, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 2})
    check({"n": 5, "edges": [], "k": 5})   # no edges: max clique 1
    check({"n": 5, "edges": [], "k": 1})
    # Complete graph K5.
    complete = [[u, v] for u in range(5) for v in range(u + 1, 5)]
    check({"n": 5, "edges": complete, "k": 5})
    check({"n": 5, "edges": complete, "k": 6})
    # Reversed edge orientation is allowed (same undirected edge).
    check({"n": 3, "edges": [[1, 0], [1, 2]], "k": 2})
    check({"n": 3, "edges": [[1, 0], [1, 2]], "k": 3})

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = run_tests()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for inst, red, exp, got in failures[:10]:
        print("FAIL:", inst, "->", red, "expected", exp, "got", got)
    assert not failures, f"{len(failures)} failures"
    print("ALL TESTS PASSED")
