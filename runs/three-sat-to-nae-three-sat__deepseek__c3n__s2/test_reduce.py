"""Tests for the 3-SAT -> NAE-3-SAT reduction in reduce.py.

problems.py provides no solvers, so we implement brute-force solvers for both
problems directly from the docstrings, then compare answers on many small
instances (exhaustive and random).
"""

from __future__ import annotations

import itertools
import random

from problems import NaeThreeSat, ThreeSat
from reduce import reduce


def sat_solve(instance: dict) -> bool:
    """Brute-force 3-SAT solver."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # bits[v-1] is the value of variable v
        if all(
            any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def nae_solve(instance: dict) -> bool:
    """Brute-force NAE-3-SAT solver."""
    NaeThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            values = [bits[abs(lit) - 1] == (lit > 0) for lit in clause]
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


def all_3sat_instances(m: int, max_clauses: int):
    """Yield all 3-SAT instances over m variables with up to max_clauses clauses."""
    lits = [v for v in range(1, m + 1)] + [-v for v in range(1, m + 1)]
    # all valid clauses: 3 literals on 3 distinct variables
    clauses = []
    for combo in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, combo)])
    # all multisets of clauses up to max_clauses (clause order irrelevant)
    for r in range(0, max_clauses + 1):
        for chosen in itertools.combinations_with_replacement(clauses, r):
            yield {"num_vars": m, "clauses": [list(c) for c in chosen]}


def check(instance: dict) -> None:
    expected = sat_solve(instance)
    reduced = reduce(instance)
    got = nae_solve(reduced)
    assert got == expected, (
        f"MISMATCH\nsource={instance}\nsource_sat={expected}\n"
        f"reduced={reduced}\nreduced_nae={got}"
    )


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # --- Edge cases: no clauses, various m (including m = 0) ---
    for m in range(0, 5):
        run({"num_vars": m, "clauses": []})

    # --- Exhaustive small instances ---
    # m=3 with up to 3 clauses (all valid 3-var clauses)
    for inst in all_3sat_instances(3, 3):
        run(inst)
    # m=4 with up to 2 clauses
    for inst in all_3sat_instances(4, 2):
        run(inst)

    # --- Random instances ---
    rng = random.Random(12345)
    for _ in range(400):
        m = rng.randint(3, 6)
        nclauses = rng.randint(0, 8)
        clauses = []
        for _ in range(nclauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
        run({"num_vars": m, "clauses": clauses})

    # --- Duplicate clauses / unused variables ---
    run({"num_vars": 5, "clauses": [[1, 2, 3], [1, 2, 3], [-1, -2, -3]]})
    run({"num_vars": 6, "clauses": [[1, 2, 3]]})
    run({"num_vars": 6, "clauses": [[-1, -2, -3]]})

    # --- A known unsatisfiable instance (all 8 clauses over 3 vars) ---
    unsat = []
    for signs in itertools.product([1, -1], repeat=3):
        unsat.append([s * v for s, v in zip(signs, (1, 2, 3))])
    run({"num_vars": 3, "clauses": unsat})

    # --- A known satisfiable instance ---
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})

    # --- Verify the reduced instance is a valid NAE instance ---
    r = reduce({"num_vars": 4, "clauses": [[1, 2, 3], [-1, 4, -2]]})
    NaeThreeSat.validate(r)
    assert r["num_vars"] == 4 + 2 + 1
    assert len(r["clauses"]) == 4

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
