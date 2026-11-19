"""Tests comparing brute-force SAT and Clique answers on small instances."""

import itertools
import random

from problems import Sat, Clique
from reduce import reduce


# --------------------------- brute force solvers ---------------------------

def sat_solve(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # bits[v-1] is the truth value of variable v
        if all(
            any((lit > 0 and bits[abs(lit) - 1]) or (lit < 0 and not bits[abs(lit) - 1])
                for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def clique_solve(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    for combo in itertools.combinations(range(n), k):
        if all(adj[a][b] for a, b in itertools.combinations(combo, 2)):
            return True
    return False


# --------------------------- instance generators ---------------------------

def random_sat(rng):
    m = rng.randint(0, 4)
    num_clauses = rng.randint(0, 5)
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, 3) if m > 0 else 0
        clause = []
        for _ in range(length):
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_sat():
    """Exhaustive-ish enumeration of tiny formulas."""
    instances = []
    # num_vars 0..2, clauses drawn from a small pool of possible clauses
    for m in range(0, 3):
        pool = [[]]
        if m >= 1:
            pool += [[1], [-1], [1, -1], [1, 1]]
        if m >= 2:
            pool += [[2], [-2], [1, 2], [-1, 2], [1, -2], [-1, -2]]
        for r in range(0, 4):
            for combo in itertools.product(pool, repeat=r):
                instances.append({"num_vars": m, "clauses": [list(c) for c in combo]})
    return instances


def main():
    tests_run = 0
    tests_passed = 0

    # Deterministic exhaustive small tests
    for inst in all_small_sat():
        Sat.validate(inst)
        red = reduce(inst)
        Clique.validate(red)
        expected = sat_solve(inst)
        got = clique_solve(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", inst, "->", red, "expected", expected, "got", got)

    # Randomized tests
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_sat(rng)
        Sat.validate(inst)
        red = reduce(inst)
        Clique.validate(red)
        expected = sat_solve(inst)
        got = clique_solve(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("FAIL", inst, "->", red, "expected", expected, "got", got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
