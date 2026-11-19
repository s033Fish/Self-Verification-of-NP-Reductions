"""Brute-force solvers and randomized tests for the 3-SAT -> Dominating Set reduction."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def sat_solve(instance):
    """Brute force 3-SAT: True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            if not any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                       for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def ds_solve(instance):
    """Brute force Dominating Set: True iff a dominating set of size <= k exists."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    vertices = list(range(n))
    for size in range(0, k + 1):
        for combo in itertools.combinations(vertices, size):
            chosen = set(combo)
            dominated = set(chosen)
            for u in chosen:
                dominated |= adj[u]
            if len(dominated) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Test helpers.

def validate_source(instance):
    """Minimal re-implementation of the ThreeSat format checks."""
    assert set(instance) == {"num_vars", "clauses"}
    m = instance["num_vars"]
    assert isinstance(m, int) and m >= 0
    for clause in instance["clauses"]:
        assert len(clause) == 3
        assert len({abs(l) for l in clause}) == 3
        for l in clause:
            assert l != 0 and abs(l) <= m


def validate_target(instance):
    """Minimal re-implementation of the DominatingSet format checks."""
    assert set(instance) == {"n", "edges", "k"}
    n = instance["n"]
    assert isinstance(n, int) and n >= 0
    assert isinstance(instance["k"], int)
    seen = set()
    for e in instance["edges"]:
        assert isinstance(e, list) and len(e) == 2
        u, v = e
        assert 0 <= u < n and 0 <= v < n and u != v
        key = frozenset((u, v))
        assert key not in seen
        seen.add(key)


def random_source(rng, max_vars=4, max_clauses=5):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        if m < 3:
            break
        vars_ = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vars_]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_random=2000, seed=12345):
    rng = random.Random(seed)
    tests_run = 0
    tests_passed = 0

    # Hand-picked edge cases.
    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 1, 2], [-4, -1, -2]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
    ]

    instances = fixed + [random_source(rng) for _ in range(num_random)]

    for src in instances:
        validate_source(src)
        tgt = reduce(src)
        validate_target(tgt)
        expected = sat_solve(src)
        got = ds_solve(tgt)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH:", src, "->", tgt, "sat=", expected, "ds=", got)

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed, "some tests failed"
    print("ALL TESTS PASSED")
