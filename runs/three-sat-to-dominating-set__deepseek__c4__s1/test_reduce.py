"""Tests for the 3-SAT -> Dominating Set reduction in reduce.py.

problems.py provides no solvers, so this file implements brute-force
solvers for both problems directly from the definitions and compares them
on many small instances (including exhaustive families and edge cases).
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_solve(instance) -> bool:
    """Brute force 3-SAT over all assignments of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(
            any((literal > 0) == bits[abs(literal) - 1] for literal in clause)
            for clause in clauses
        ):
            return True
    return False


def ds_solve(instance) -> bool:
    """Brute force Dominating Set: is there a set of size <= k dominating?"""
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
    for size in range(0, k + 1):
        for chosen in itertools.combinations(range(n), size):
            dominated = set(chosen)
            for u in chosen:
                dominated |= adj[u]
            if len(dominated) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators.

def all_clauses(m):
    """All 3-clauses over variables 1..m (3 distinct variables each)."""
    clauses = []
    for variables in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([variables[i] * signs[i] for i in range(3)])
    return clauses


def random_formula(m, num_clauses, rng):
    clauses = []
    for _ in range(num_clauses):
        variables = rng.sample(range(1, m + 1), 3)
        clauses.append([v * rng.choice([1, -1]) for v in variables])
    return {"num_vars": m, "clauses": clauses}


def check(formula):
    """Return True iff reduction preserves the answer; also validate formats."""
    problems.ThreeSat.validate(formula)
    reduced = reduce(formula)
    problems.DominatingSet.validate(reduced)
    return sat_solve(formula) == ds_solve(reduced)


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(name, formula):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ok = check(formula)
        except Exception as exc:  # noqa: BLE001
            failures.append((name, formula, repr(exc)))
            return
        if ok:
            tests_passed += 1
        else:
            failures.append((name, formula, "answer mismatch"))

    # Edge cases: no clauses for m = 0, 1, 2 (all satisfiable).
    for m in range(0, 4):
        run(f"no-clauses m={m}", {"num_vars": m, "clauses": []})

    # Exhaustive over all clause subsets for m = 3 (256 formulas).
    clauses3 = all_clauses(3)
    for mask in range(1 << len(clauses3)):
        formula = {
            "num_vars": 3,
            "clauses": [clauses3[i] for i in range(len(clauses3)) if mask >> i & 1],
        }
        run(f"exhaustive m=3 mask={mask}", formula)

    # Full unsat formula for m = 3 and m = 4 (all clauses present).
    for m in (3, 4):
        run(f"all-clauses m={m}", {"num_vars": m, "clauses": all_clauses(m)})

    # Duplicate clauses.
    run("duplicates", {"num_vars": 3, "clauses": [[1, 2, 3]] * 5})
    run("duplicates-unsat", {"num_vars": 3, "clauses": all_clauses(3) * 2})

    # Variables that do not appear in any clause.
    run("unused-vars", {"num_vars": 5, "clauses": [[1, 2, 3]]})

    # Random small instances.
    rng = random.Random(20240607)
    for m in range(3, 9):
        for _ in range(120):
            num_clauses = rng.randint(0, 16)
            run(f"random m={m}", random_formula(m, num_clauses, rng))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for name, formula, reason in failures[:10]:
        print("FAIL", name, reason, formula)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run_count, pass_count, fails = main()
    assert not fails, f"{len(fails)} failing tests"
    print("ALL TESTS PASSED")
