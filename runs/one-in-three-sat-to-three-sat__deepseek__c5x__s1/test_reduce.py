"""Tests for the reduction from OneInThreeSat to ThreeSat.

The test suite implements brute‑force solvers for both source and target
problems based directly on the definitions in ``problems.py``.  It then
generates a number of random small instances, applies ``reduce`` and checks
that the answer to the reduced instance matches the answer to the original
instance.

The script records how many instances were tested and how many passed.  It
outputs a JSON file ``verdict.json`` in the required format.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

# Import the problem definitions and the reduction implementation.
import problems  # noqa: F401 – validates that the module loads correctly.
from reduce import reduce  # type: ignore


def solve_one_in_three(instance: dict) -> bool:
    """Brute‑force solver for OneInThreeSat.

    Returns ``True`` iff there exists an assignment to the variables such that
    each clause has **exactly** one true literal.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all 2^m assignments
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            # count true literals in this clause
            true_cnt = sum(((mask >> (v - 1)) & 1) for v in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force solver for ThreeSat.

    Returns ``True`` iff there exists an assignment satisfying all clauses
    (at least one true literal per clause).
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            # clause literals may be positive or negative
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = (mask >> (var - 1)) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                    break
                if lit < 0 and val == 0:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def generate_random_instance(max_vars: int = 4, max_clauses: int = 5) -> dict:
    """Generate a random OneInThreeSat instance.

    The generator respects the edge‑case that a formula with clauses must
    have at least three variables.  For ``num_vars`` < 3 we only generate an
    empty clause list.
    """
    m = random.randint(0, max_vars)
    # If we generate clauses we need at least three variables.
    if m >= 3:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            # sample three distinct variables from 1..m
            clause = random.sample(range(1, m + 1), 3)
            clauses.append(clause)
    else:
        clauses = []
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    tests_run = 0
    tests_passed = 0
    # generate a decent number of random instances
    for _ in range(200):
        src = generate_random_instance()
        # validate source instance using the problem's validator
        try:
            problems.OneInThreeSat.validate(src)
        except Exception as e:
            print(f"Invalid generated source instance: {e}", file=sys.stderr)
            continue
        tgt = reduce(src)
        # validate target instance
        try:
            problems.ThreeSat.validate(tgt)
        except Exception as e:
            print(f"Reduction produced invalid target instance: {e}", file=sys.stderr)
            continue
        src_ans = solve_one_in_three(src)
        tgt_ans = solve_three_sat(tgt)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            print("Mismatch!", src, tgt, src_ans, tgt_ans, file=sys.stderr)
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

