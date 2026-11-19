"""Tests for the 3-SAT -> Vertex Cover reduction.

Includes independent brute-force solvers for both problems, then compares
their answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    SOURCE.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_vertex_cover(instance):
    """Return True iff the graph has a vertex cover of size <= k.

    Exact bounded-search-tree algorithm (branch on an uncovered edge).
    """
    TARGET.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True

    def search(remaining, budget):
        if not remaining:
            return True
        if budget == 0:
            return False
        u, v = remaining[0]
        # Branch: include u or include v.
        without_u = [e for e in remaining if u not in e]
        if search(without_u, budget - 1):
            return True
        without_v = [e for e in remaining if v not in e]
        return search(without_v, budget - 1)

    return search(edges, k)


# ----------------------------------------------------------------------
# Helpers

def random_three_sat(rng, num_vars, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def check(instance):
    expected = solve_three_sat(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    got = solve_vertex_cover(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            check(instance)
            tests_passed += 1
        except AssertionError as exc:
            failures.append((label, exc))
            print(f"FAIL {label}: {exc}")

    # --- Explicit edge cases -----------------------------------------
    run({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    run({"num_vars": 1, "clauses": []}, "m=1 no clauses")
    run({"num_vars": 5, "clauses": []}, "m=5 no clauses")

    # Unsatisfiable: all 8 clauses over 3 variables.
    all_clauses = [
        [s[0] * 1, s[1] * 2, s[2] * 3]
        for s in itertools.product([1, -1], repeat=3)
    ]
    run({"num_vars": 3, "clauses": all_clauses}, "unsat all 8 clauses")

    run({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two clauses")
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    run({"num_vars": 4, "clauses": [[1, 2, 3]]}, "unused variable")

    # --- Random tests (sizes kept small for brute force) -------------
    rng = random.Random(12345)
    for num_vars in range(3, 5):
        for num_clauses in range(0, 5):
            for trial in range(15):
                inst = random_three_sat(rng, num_vars, num_clauses)
                run(inst, f"random m={num_vars} c={num_clauses} t={trial}")

    # --- Exhaustive over sign patterns, m=3, c in {1,2} --------------
    for num_clauses in range(1, 3):
        for signs in itertools.product([1, -1], repeat=3 * num_clauses):
            clauses = [
                [signs[3 * ci + j] * (j + 1) for j in range(3)]
                for ci in range(num_clauses)
            ]
            run({"num_vars": 3, "clauses": clauses}, "exhaustive m=3")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    return tests_run, tests_passed, len(failures)


if __name__ == "__main__":
    main()
