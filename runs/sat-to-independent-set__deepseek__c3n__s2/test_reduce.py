"""Tests for the SAT -> Independent Set reduction in reduce.py.

Includes independent brute-force solvers for both problems, written from the
definitions in problems.py, plus randomized comparison tests.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)


def sat_solve(instance) -> bool:
    """True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        # bits[v-1] is the value of variable v.
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def is_solve(instance) -> bool:
    """True iff the graph has an independent set of size >= k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edges = {frozenset(e) for e in instance["edges"]}
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            s = set(combo)
            if all(not (frozenset((u, v)) in edges) for u, v in itertools.combinations(combo, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Helpers


def check(instance, label=""):
    problems.Sat.validate(instance)
    out = reduce(instance)
    problems.IndependentSet.validate(out)
    a = sat_solve(instance)
    b = is_solve(out)
    assert a == b, f"MISMATCH {label}: sat={a} is={b}\n  in={instance}\n  out={out}"
    return a


def random_sat(rng, max_vars=4, max_clauses=4, max_len=3):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
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
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            check(instance, label)
            tests_passed += 1
        except AssertionError as exc:
            failures.append(str(exc))

    # --- explicit edge cases ---
    run({"num_vars": 0, "clauses": []}, "no vars, no clauses")
    run({"num_vars": 3, "clauses": []}, "no clauses")
    run({"num_vars": 0, "clauses": [[]]}, "empty clause, no vars")
    run({"num_vars": 2, "clauses": [[1], [-1]]}, "v and -v")
    run({"num_vars": 2, "clauses": [[1, 1], [-1]]}, "repeated literal")
    run({"num_vars": 2, "clauses": [[1, -1]]}, "tautology")
    run({"num_vars": 1, "clauses": [[1], [1], [1]]}, "duplicate clauses")
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two clauses")
    run({"num_vars": 3, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]}, "unsat 2-cnf")
    run({"num_vars": 1, "clauses": [[1, -1], []]}, "tautology plus empty")
    run({"num_vars": 4, "clauses": [[1], [2], [3], [4]]}, "all units")
    run({"num_vars": 4, "clauses": [[-1], [-2], [-3], [-4]]}, "all neg units")

    # --- randomized ---
    rng = random.Random(12345)
    for i in range(4000):
        run(random_sat(rng), f"random {i}")

    # slightly larger random instances
    for i in range(300):
        run(random_sat(rng, max_vars=6, max_clauses=6, max_len=4), f"random-large {i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for f in failures[:10]:
            print(f)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
