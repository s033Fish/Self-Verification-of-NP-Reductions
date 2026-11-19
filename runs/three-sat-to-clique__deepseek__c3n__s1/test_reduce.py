"""Tests comparing brute-force answers on 3-SAT instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import solve_three_sat, solve_clique

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    # Source must be valid.
    SOURCE.validate(instance)
    out = reduce(instance)
    # Target must be valid.
    TARGET.validate(out)
    expected = solve_three_sat(instance)
    got = solve_clique(out)
    assert got == expected, (
        f"mismatch {label}: instance={instance} expected={expected} "
        f"got={got} reduced={out}"
    )
    tests_passed += 1


def random_instance(rng, max_vars=5, max_clauses=5):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    if nclauses > 0:
        m = max(m, 3)
    clauses = []
    for _ in range(nclauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    # --- Explicit edge cases -------------------------------------------------
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "empty m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    # Unsatisfiable: all 8 clauses over 3 vars.
    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([signs[i] * (i + 1) for i in range(3)])
    check({"num_vars": 3, "clauses": all_clauses}, "unsat 3 vars")
    # Variables that never appear.
    check({"num_vars": 10, "clauses": [[1, 2, 3]]}, "unused vars")

    # --- Exhaustive-ish random testing --------------------------------------
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng), "random")

    # More clauses than variables, forcing unsat often.
    rng2 = random.Random(999)
    for _ in range(1000):
        m = rng2.randint(3, 4)
        nclauses = rng2.randint(0, 10)
        clauses = []
        for _ in range(nclauses):
            vs = rng2.sample(range(1, m + 1), 3)
            clause = [v if rng2.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
        check({"num_vars": m, "clauses": clauses}, "dense")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
