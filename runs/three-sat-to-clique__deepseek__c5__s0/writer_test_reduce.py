"""Tests for the 3-SAT -> Clique reduction in reduce.py.

Includes brute-force solvers for both problems written from the
definitions in problems.py, plus exhaustive and randomized tests.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)

def solve_three_sat(instance):
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def max_clique_size(instance):
    """Exact maximum clique size via branch and bound (bitmasks)."""
    n = instance["n"]
    adj = [0] * n
    for u, v in instance["edges"]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    best = 0

    def expand(cand, size):
        nonlocal best
        if size > best:
            best = size
        if cand == 0:
            return
        c = cand
        while c:
            if size + bin(c).count("1") <= best:
                return
            v = (c & -c).bit_length() - 1
            c &= c - 1
            expand(cand & adj[v], size + 1)

    expand((1 << n) - 1, 0)
    return best


def solve_clique(instance):
    """True iff the graph has a clique of size >= k."""
    k = instance["k"]
    if k <= 0:
        return True
    if k > instance["n"]:
        return False
    return max_clique_size(instance) >= k


# ----------------------------------------------------------------------
# Test helpers

tests_run = 0
tests_passed = 0


def check(condition, message):
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        raise AssertionError(message)


def check_reduction(instance, label):
    """Validate, reduce, validate, and compare brute-force answers."""
    ThreeSat.validate(instance)
    target = reduce(instance)
    Clique.validate(target)
    expected = solve_three_sat(instance)
    got = solve_clique(target)
    check(
        expected == got,
        f"{label}: source={instance} expected={expected} "
        f"target={target} got={got}",
    )


def all_three_sat_instances(max_vars, max_clauses):
    """Yield many small valid 3-SAT instances."""
    for m in range(0, max_vars + 1):
        clauses_pool = []
        if m >= 3:
            for combo in itertools.combinations(range(1, m + 1), 3):
                for signs in itertools.product([1, -1], repeat=3):
                    clauses_pool.append([s * v for s, v in zip(signs, combo)])
        for r in range(0, max_clauses + 1):
            for chosen in itertools.combinations_with_replacement(clauses_pool, r):
                yield {"num_vars": m, "clauses": [list(c) for c in chosen]}


# ----------------------------------------------------------------------
# Tests

def test_empty_formula():
    check_reduction({"num_vars": 0, "clauses": []}, "empty m=0")
    check_reduction({"num_vars": 5, "clauses": []}, "empty m=5")
    t = reduce({"num_vars": 5, "clauses": []})
    check(t == {"n": 0, "edges": [], "k": 0}, f"empty target {t}")


def test_single_clause():
    for clause in ([1, 2, 3], [1, 2, -3], [-1, -2, -3]):
        check_reduction({"num_vars": 3, "clauses": [clause]}, f"single {clause}")


def test_unsatisfiable_small():
    clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        clauses.append([s * v for s, v in zip(signs, (1, 2, 3))])
    inst = {"num_vars": 3, "clauses": clauses}
    check(not solve_three_sat(inst), "all-8-clauses should be UNSAT")
    check_reduction(inst, "all 8 clauses")


def test_duplicate_clauses():
    inst = {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}
    check_reduction(inst, "duplicates")


def test_unused_variables():
    inst = {"num_vars": 6, "clauses": [[1, 2, 3], [-1, -2, -3]]}
    check_reduction(inst, "unused vars")


def test_exhaustive_small():
    count = 0
    for inst in all_three_sat_instances(max_vars=4, max_clauses=3):
        check_reduction(inst, f"exhaustive #{count}")
        count += 1
    check(count > 0, "exhaustive produced instances")


def test_random():
    rng = random.Random(12345)
    for trial in range(1000):
        m = rng.randint(3, 8)
        num_clauses = rng.randint(0, 6)
        clauses = []
        for _ in range(num_clauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
        inst = {"num_vars": m, "clauses": clauses}
        check_reduction(inst, f"random trial {trial}")


def test_random_unsat_heavy():
    rng = random.Random(999)
    for trial in range(1000):
        m = rng.randint(3, 5)
        num_clauses = rng.randint(3, 8)
        clauses = []
        for _ in range(num_clauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
        inst = {"num_vars": m, "clauses": clauses}
        check_reduction(inst, f"unsat-heavy trial {trial}")


def test_polynomial_size():
    inst = {"num_vars": 10, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
    t = reduce(inst)
    check(t["n"] == 9, f"n should be 9, got {t['n']}")
    check(t["k"] == 3, f"k should be 3, got {t['k']}")
    check(len(t["edges"]) <= t["n"] * t["n"], "edges bounded")


def main():
    test_empty_formula()
    test_single_clause()
    test_unsatisfiable_small()
    test_duplicate_clauses()
    test_unused_variables()
    test_exhaustive_small()
    test_random()
    test_random_unsat_heavy()
    test_polynomial_size()
    print(f"ALL TESTS PASSED: {tests_passed}/{tests_run}")


if __name__ == "__main__":
    main()
