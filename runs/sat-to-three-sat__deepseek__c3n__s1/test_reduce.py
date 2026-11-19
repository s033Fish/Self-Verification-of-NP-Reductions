"""Tests for the SAT -> 3-SAT reduction in reduce.py.

We implement brute-force solvers for both problems directly from the
docstrings in problems.py and compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import Sat, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_solve(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assignment = {v + 1: bits[v] for v in range(m)}
        if all(
            any(assignment[abs(lit)] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def three_sat_solve(instance):
    # Same semantics; validate structure too.
    ThreeSat.validate(instance)
    return sat_solve(instance)


# ----------------------------------------------------------------------
# Instance generation.

def all_sat_instances(max_vars=3, max_clauses=3, max_len=3):
    """Enumerate a broad family of small SAT instances."""
    for m in range(0, max_vars + 1):
        lits = [l for v in range(1, m + 1) for l in (v, -v)]
        # possible clauses of length 0..max_len (with repetition allowed)
        clause_pool = [[]]
        for length in range(1, max_len + 1):
            clause_pool.extend(itertools.combinations_with_replacement(lits, length))
        for num_clauses in range(0, max_clauses + 1):
            for clauses in itertools.combinations_with_replacement(clause_pool, num_clauses):
                yield {"num_vars": m, "clauses": [list(c) for c in clauses]}


def random_sat_instance(rng, max_vars=5, max_clauses=6, max_len=5):
    m = rng.randint(0, max_vars)
    lits = [l for v in range(1, m + 1) for l in (v, -v)]
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, max_len)
        if length == 0 or not lits:
            clauses.append([])
        else:
            clauses.append([rng.choice(lits) for _ in range(length)])
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests.

def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            Sat.validate(instance)
            expected = sat_solve(instance)
            reduced = reduce(instance)
            ThreeSat.validate(reduced)  # target must be well-formed
            got = three_sat_solve(reduced)
            assert got == expected, (
                f"{label}: source={instance} expected={expected} "
                f"reduced={reduced} got={got}"
            )
            tests_passed += 1
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: {exc}")

    # 1. Hand-picked edge cases.
    check({"num_vars": 0, "clauses": []}, "empty formula m=0")
    check({"num_vars": 5, "clauses": []}, "no clauses")
    check({"num_vars": 1, "clauses": [[]]}, "empty clause")
    check({"num_vars": 3, "clauses": [[1], [2], [3]]}, "three units")
    check({"num_vars": 2, "clauses": [[1], [-1]]}, "contradictory units")
    check({"num_vars": 3, "clauses": [[1, -1]]}, "tautology only")
    check({"num_vars": 3, "clauses": [[1, -1], []]}, "tautology plus empty")
    check({"num_vars": 4, "clauses": [[1, 2], [-1, -2]]}, "two 2-clauses")
    check({"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]}, "one long clause")
    check({"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6], [-1], [-2], [-3], [-4], [-5], [-6]]},
          "long clause forced false")
    check({"num_vars": 4, "clauses": [[1, 1, 1], [1, 1, 1]]}, "repeated literals")
    check({"num_vars": 4, "clauses": [[1, -1, 2, 3]]}, "tautology with others")

    # 2. Exhaustive small instances.
    for instance in all_sat_instances(max_vars=3, max_clauses=3, max_len=3):
        check(instance, "exhaustive")

    # 3. Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_sat_instance(rng), "random")

    # 4. Random instances biased toward satisfiable/unsatisfiable mixes.
    rng2 = random.Random(999)
    for _ in range(2000):
        m = rng2.randint(1, 6)
        clauses = []
        for _ in range(rng2.randint(1, 8)):
            length = rng2.randint(1, 4)
            clauses.append([rng2.choice([v, -v]) for v in rng2.sample(range(1, m + 1), min(length, m))])
        check({"num_vars": m, "clauses": clauses}, "random2")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    total, passed, fails = run_tests()
    print(f"tests_run={total} tests_passed={passed}")
    for f in fails[:20]:
        print("FAIL:", f)
    assert not fails, f"{len(fails)} failures"
    print("ALL TESTS PASSED")
