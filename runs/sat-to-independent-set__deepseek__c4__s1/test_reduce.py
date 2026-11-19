"""Tests for the SAT -> Independent Set reduction."""

from __future__ import annotations

import random

from problems import Sat, IndependentSet
from reduce import reduce
from solvers import sat_solve, is_solve

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    Sat.validate(instance)
    out = reduce(instance)
    IndependentSet.validate(out)
    expected = sat_solve(instance)
    got = is_solve(out)
    assert expected == got, (
        f"mismatch {label}: source={instance} reduced={out} "
        f"sat={expected} is={got}"
    )
    tests_passed += 1


def random_instance(rng, max_vars, max_clauses, max_len):
    m = rng.randint(0, max_vars)
    t = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(t):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    # Explicit edge cases.
    check({"num_vars": 0, "clauses": []}, "empty formula")
    check({"num_vars": 0, "clauses": [[]]}, "empty clause, no vars")
    check({"num_vars": 3, "clauses": []}, "no clauses")
    check({"num_vars": 3, "clauses": [[]]}, "one empty clause")
    check({"num_vars": 3, "clauses": [[1], [-1]]}, "contradiction")
    check({"num_vars": 3, "clauses": [[1], [1], [1]]}, "duplicate clauses")
    check({"num_vars": 3, "clauses": [[1, 1, 1]]}, "repeated literal")
    check({"num_vars": 3, "clauses": [[1, -1]]}, "tautology")
    check({"num_vars": 3, "clauses": [[1, 2], [-1, 2], [-2]]}, "small sat")
    check({"num_vars": 2, "clauses": [[1], [2], [-1, -2]]}, "unsat")
    check({"num_vars": 1, "clauses": [[1], [-1]]}, "unsat 1 var")

    rng = random.Random(12345)
    for i in range(4000):
        inst = random_instance(rng, max_vars=4, max_clauses=5, max_len=4)
        check(inst, f"random-small-{i}")

    rng = random.Random(999)
    for i in range(600):
        inst = random_instance(rng, max_vars=6, max_clauses=7, max_len=5)
        check(inst, f"random-medium-{i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
