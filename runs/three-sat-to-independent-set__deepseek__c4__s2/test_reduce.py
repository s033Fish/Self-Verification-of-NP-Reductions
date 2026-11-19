"""Tests for reduce.py: compare brute-force answers on small instances."""

from __future__ import annotations

import itertools
import random
from functools import lru_cache

from problems import ThreeSat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.

def solve_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {v + 1: bits[v] for v in range(m)}
        ok = True
        for clause in clauses:
            if not any(
                (lit > 0 and assignment[abs(lit)]) or (lit < 0 and not assignment[abs(lit)])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u

    @lru_cache(maxsize=None)
    def max_is(mask: int) -> int:
        if mask == 0:
            return 0
        # Pick lowest set bit v.
        v = (mask & -mask).bit_length() - 1
        # Option 1: exclude v.
        best = max_is(mask & ~(1 << v))
        # Option 2: include v, remove v and its neighbours.
        best = max(best, 1 + max_is(mask & ~(1 << v) & ~adj[v]))
        return best

    return max_is((1 << n) - 1) >= k


def check(instance: dict) -> bool:
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)
    src = solve_three_sat(instance)
    tgt = solve_independent_set(reduced)
    assert src == tgt, (instance, reduced, src, tgt)
    return src


# ----------------------------------------------------------------------
# Test cases.

tests_run = 0
tests_passed = 0


def run(name: str, fn) -> None:
    global tests_run, tests_passed
    tests_run += 1
    try:
        fn()
    except AssertionError as exc:
        print(f"FAIL {name}: {exc}")
    else:
        tests_passed += 1


# Edge cases.
def t_empty_zero():
    assert check({"num_vars": 0, "clauses": []}) is True


def t_empty_some_vars():
    assert check({"num_vars": 5, "clauses": []}) is True


def t_single_clause_sat():
    assert check({"num_vars": 3, "clauses": [[1, 2, 3]]}) is True


def t_single_clause_neg():
    assert check({"num_vars": 3, "clauses": [[-1, -2, -3]]}) is True


def t_two_clauses():
    # (x1 or x2 or x3) and (~x1 or ~x2 or ~x3) is satisfiable
    assert check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}) is True


def t_all_eight():
    # all 8 clauses over 3 vars -> unsatisfiable
    clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        clauses.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    assert check({"num_vars": 3, "clauses": clauses}) is False


def t_duplicate_clauses():
    assert check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}) is True


def t_unused_vars():
    assert check({"num_vars": 6, "clauses": [[1, 2, 3]]}) is True


def t_forced_unsat():
    # All 8 clauses over vars 1,2,3 -> unsatisfiable; add extra clauses over
    # variable 4 to make sure extra variables do not break the reduction.
    clauses = [
        [1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
        [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3],
        [4, 1, 2], [-4, 1, 2],
    ]
    assert check({"num_vars": 4, "clauses": clauses}) is False


# Random tests.
def random_instance(rng, max_vars, max_clauses):
    m = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def t_random():
    rng = random.Random(12345)
    for _ in range(500):
        inst = random_instance(rng, max_vars=5, max_clauses=7)
        check(inst)


def t_random_dense_small():
    rng = random.Random(999)
    for _ in range(300):
        inst = random_instance(rng, max_vars=3, max_clauses=10)
        check(inst)


def t_random_many_vars():
    rng = random.Random(4242)
    for _ in range(200):
        inst = random_instance(rng, max_vars=8, max_clauses=4)
        check(inst)


run("empty_zero", t_empty_zero)
run("empty_some_vars", t_empty_some_vars)
run("single_clause_sat", t_single_clause_sat)
run("single_clause_neg", t_single_clause_neg)
run("two_clauses", t_two_clauses)
run("all_eight", t_all_eight)
run("duplicate_clauses", t_duplicate_clauses)
run("unused_vars", t_unused_vars)
run("forced_unsat", t_forced_unsat)
run("random", t_random)
run("random_dense_small", t_random_dense_small)
run("random_many_vars", t_random_many_vars)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"
