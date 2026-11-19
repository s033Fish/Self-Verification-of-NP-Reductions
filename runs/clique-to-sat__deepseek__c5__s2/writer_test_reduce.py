"""Tests for the Clique -> SAT reduction in reduce.py.

Includes independent brute-force solvers for both problems (from the
definitions in problems.py) and compares their answers on many small
random source instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of the reduction)

def solve_clique(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

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
            if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def _simplify(clauses, assign):
    """Return (status, new_clauses): status False -> unsat, True -> clauses."""
    new_clauses = []
    for clause in clauses:
        satisfied = False
        rest = set()
        for lit in clause:
            v = abs(lit)
            if v in assign:
                if (lit > 0) == assign[v]:
                    satisfied = True
                    break
            else:
                rest.add(lit)
        if satisfied:
            continue
        if not rest:
            return False, None
        new_clauses.append(rest)
    return True, new_clauses


def solve_sat(instance) -> bool:
    """Complete DPLL solver (exhaustive search with unit propagation)."""
    num_vars = instance["num_vars"]
    clauses = []
    for clause in instance["clauses"]:
        s = set(clause)
        if any(-lit in s for lit in s):
            continue  # tautology
        clauses.append(s)
    return _dpll(clauses, {})


def _dpll(clauses, assign):
    assign = dict(assign)
    while True:
        ok, clauses = _simplify(clauses, assign)
        if not ok:
            return False
        if not clauses:
            return True
        # unit propagation
        units = [next(iter(c)) for c in clauses if len(c) == 1]
        if not units:
            break
        for lit in units:
            v = abs(lit)
            val = lit > 0
            if v in assign and assign[v] != val:
                return False
            assign[v] = val
    # choose a literal from the shortest clause
    clause = min(clauses, key=len)
    lit = next(iter(clause))
    for val in (True, False):
        trial = dict(assign)
        trial[abs(lit)] = val if lit > 0 else not val
        if _dpll(clauses, trial):
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def random_clique_instance(rng, max_n=6):
    n = rng.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(possible)
    m = rng.randint(0, len(possible))
    edges = [list(e) for e in possible[:m]]
    k = rng.randint(-1, n + 2)
    return {"n": n, "edges": edges, "k": k}


def check(instance):
    Clique.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = solve_clique(instance)
    got = solve_sat(reduced)
    assert got == expected, (instance, reduced, expected, got)
    return expected


# ----------------------------------------------------------------------
# Tests

def test_edge_cases():
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 3},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 4},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 5},
    ]
    for inst in cases:
        check(inst)


def test_random():
    rng = random.Random(12345)
    for _ in range(400):
        check(random_clique_instance(rng, max_n=5))


def test_random_larger():
    rng = random.Random(999)
    for _ in range(80):
        check(random_clique_instance(rng, max_n=8))


def test_reduction_size_polynomial_sanity():
    rng = random.Random(7)
    n = 12
    edges = [[u, v] for u in range(n) for v in range(u + 1, n) if rng.random() < 0.5]
    inst = {"n": n, "edges": edges, "k": 5}
    reduced = reduce(inst)
    assert reduced["num_vars"] == 5 * n


if __name__ == "__main__":
    tests = [
        test_edge_cases,
        test_random,
        test_random_larger,
        test_reduction_size_polynomial_sanity,
    ]
    passed = 0
    total = 0
    for test in tests:
        total += 1
        test()
        passed += 1
        print(f"PASS {test.__name__}")
    print(f"{passed}/{total} tests passed")
