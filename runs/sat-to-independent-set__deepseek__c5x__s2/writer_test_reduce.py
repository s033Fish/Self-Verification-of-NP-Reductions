"""Tests for reduce.py: compare brute-force answers on small instances."""

from __future__ import annotations

import itertools
import random

from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------- brute force solvers -----------------------------

def sat_solve(instance: dict) -> bool:
    """Brute force SAT: try every assignment of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assign = {v + 1: bits[v] for v in range(m)}
        if all(
            any((lit > 0) == assign[abs(lit)] for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def is_solve(instance: dict) -> bool:
    """Brute force Independent Set: try every subset of vertices."""
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k <= 0:
        return True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u not in chosen or v not in chosen for u, v in edges):
                return True
    return False


# ----------------------------- instance generators -----------------------------

def random_sat(rng: random.Random) -> dict:
    m = rng.randint(0, 5)
    n_clauses = rng.randint(0, 6)
    clauses = []
    for _ in range(n_clauses):
        length = rng.randint(0, 4)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


# ----------------------------- tests -----------------------------

def check(instance: dict) -> bool:
    Sat.validate(instance)
    reduced = reduce(instance)
    IndependentSet.validate(reduced)
    expected = sat_solve(instance)
    got = is_solve(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def test_handmade():
    cases = [
        # no clauses -> satisfiable
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        # empty clause -> unsatisfiable
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 2, "clauses": [[1], []]},
        # simple satisfiable
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        # contradiction in one clause is fine
        {"num_vars": 1, "clauses": [[1, -1]]},
        # direct contradiction across clauses
        {"num_vars": 1, "clauses": [[1], [-1]]},
        # unsatisfiable: (x) and (-x)
        {"num_vars": 2, "clauses": [[1], [-1], [2]]},
        # repeated literals
        {"num_vars": 2, "clauses": [[1, 1, 1], [-1, 2], [-2]]},
        # duplicate clauses
        {"num_vars": 2, "clauses": [[1, 2], [1, 2], [-1], [-2]]},
        # variables not all used
        {"num_vars": 5, "clauses": [[1], [2]]},
        # classic unsat 2-SAT cycle
        {"num_vars": 2, "clauses": [[1, 2], [1, -2], [-1, 2], [-1, -2]]},
    ]
    for case in cases:
        check(case)


def test_random_many():
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_sat(rng))


def test_edges_valid_no_duplicates():
    rng = random.Random(999)
    for _ in range(300):
        inst = random_sat(rng)
        red = reduce(inst)
        seen = set()
        for u, v in red["edges"]:
            assert u != v
            key = frozenset((u, v))
            assert key not in seen, (inst, red)
            seen.add(key)


if __name__ == "__main__":
    test_handmade()
    print("handmade ok")
    test_edges_valid_no_duplicates()
    print("edge validity ok")
    test_random_many()
    print("random ok")
    print("ALL TESTS PASSED")
