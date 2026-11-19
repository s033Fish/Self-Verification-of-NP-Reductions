"""Test the reduction from OneInThreeSat to ExactCover.

The script implements brute‑force solvers for both problems based on the
formal definitions in ``problems.py``. It then generates a large number of
random small instances of the source problem, validates them, runs the
reduction, validates the produced target instance and checks that the two
solvers agree on the answer.  The results are written to ``verdict.json``
as required by the task description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations

import problems  # the module containing the problem classes and validators
from reduce import reduce as reduce_instance


def solve_one_in_three_sat(instance: dict) -> bool:
    """Brute‑force solver for the source problem.

    Returns True iff there exists an assignment of the ``num_vars`` Boolean
    variables such that each clause has exactly one true literal.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: no clauses is always satisfiable.
    if not clauses:
        return True
    # Enumerate all 2^m assignments as tuples of booleans.
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # clause variables are 1‑based.
            true_count = sum(assignment[var - 1] for var in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """Brute‑force solver for Exact Cover.

    Returns True iff a sub‑collection of the given sets forms an exact cover
    of the universe ``0..u-1``.
    """
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # Pre‑convert each set to a frozenset for fast operations.
    fsets = [frozenset(s) for s in sets]
    # Iterate over all subsets of the set indices.
    for r in range(n + 1):
        for combo in combinations(range(n), r):
            covered = set()
            ok = True
            for idx in combo:
                s = fsets[idx]
                # Disjointness check.
                if covered & s:
                    ok = False
                    break
                covered |= s
            if ok and len(covered) == u:
                return True
    return False


def random_one_in_three_instance(max_vars: int, max_clauses: int) -> dict:
    """Generate a random valid instance of OneInThreeSat.

    The generator may produce duplicate clauses or variables that do not
    appear at all – both are allowed by the specification.
    """
    m = random.randint(0, max_vars)
    # Ensure that if there are clauses we have at least 3 variables.
    if m < 3:
        # With fewer than 3 variables we can only generate an instance with
        # zero clauses (which is always satisfiable).
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # Pick three distinct variables uniformly.
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    mismatches = []

    for _ in range(200):  # reasonable number of random tests
        src = random_one_in_three_instance(max_vars=5, max_clauses=5)
        # Validate source instance using the provided validator.
        try:
            problems.OneInThreeSat.validate(src)
        except Exception as e:
            print("Invalid source instance generated:", src, file=sys.stderr)
            raise

        # Compute expected answer.
        expected = solve_one_in_three_sat(src)

        # Apply reduction.
        tgt = reduce_instance(src)
        # Validate target instance.
        problems.ExactCover.validate(tgt)

        actual = solve_exact_cover(tgt)
        tests_run += 1
        if expected == actual:
            tests_passed += 1
        else:
            mismatches.append({"src": src, "tgt": tgt, "expected": expected, "actual": actual})

    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    # Write verdict.json
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

    # If there were mismatches, also dump them for debugging.
    if mismatches:
        with open("mismatches.json", "w", encoding="utf-8") as f:
            json.dump(mismatches, f, indent=2)
        sys.exit(1)

if __name__ == "__main__":
    main()
