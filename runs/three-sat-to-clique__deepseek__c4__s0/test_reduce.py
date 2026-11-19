"""Tests comparing brute-force answers on small 3-SAT instances and their reductions."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, Clique
from reduce import reduce
from solvers import solve_three_sat, solve_clique

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    Clique.validate(reduced)  # must be a well-formed Clique instance
    src = solve_three_sat(instance)
    tgt = solve_clique(reduced)
    if src == tgt:
        tests_passed += 1
    else:
        print(f"FAIL {label}: instance={instance} reduced={reduced} src={src} tgt={tgt}")


def random_instance(rng, max_vars=6, max_clauses=5):
    m = rng.randint(0, max_vars)
    n_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(n_clauses):
        if m < 3:
            # Cannot form a valid clause; skip (validator requires 3 distinct vars).
            break
        variables = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)

    # Edge cases: empty formula for various m.
    for m in [0, 1, 2, 3, 5, 8]:
        check({"num_vars": m, "clauses": []}, f"empty m={m}")

    # Small exhaustive-ish set of hand cases.
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "one clause")
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]}, "one neg clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two clauses")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, 3], [1, -2, -3]]}, "three")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [4, -1, -2]]}, "m=4")

    # Exhaustive over all formulas with m=3 and up to 2 clauses.
    lits = [1, 2, 3, -1, -2, -3]
    all_clauses = []
    for combo in itertools.combinations(range(6), 3):
        varset = {abs(lits[i]) for i in combo}
        if len(varset) == 3:
            all_clauses.append([lits[i] for i in combo])
    for c1 in all_clauses:
        check({"num_vars": 3, "clauses": [c1]}, "exh m=3 1clause")
        for c2 in all_clauses:
            check({"num_vars": 3, "clauses": [c1, c2]}, "exh m=3 2clause")

    # Random instances.
    for _ in range(3000):
        inst = random_instance(rng)
        check(inst, "random")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
