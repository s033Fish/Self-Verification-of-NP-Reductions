"""Automated tests for the reduction from OneInThreeSat to ThreeSat.

The repository provides only validation functions for the two problems and a
``reduce`` implementation.  To verify that the reduction is correct we need
brute‑force solvers for both problems and then compare the answer on a large
set of small random instances.

The script:
* implements ``solve_one_in_three`` and ``solve_three_sat`` which enumerate all
  possible truth assignments (variables are numbered from 1).
* generates random, *valid* instances of ``OneInThreeSat`` with up to 5
  variables and up to 4 clauses.  The generation respects the validation rules
  (positive literals only, three distinct variables per clause).
* for each instance runs ``reduce`` and checks that the answers of the source
  and target instance match.
* counts how many tests were executed and how many passed; the result is
  written to ``verdict.json`` as required by the task description.

The script is deliberately deterministic (uses ``random.seed(0)``) so that the
verdict is reproducible.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict

import problems
from reduce import reduce as reduce_instance


def solve_one_in_three(instance: Dict) -> bool:
    """Brute‑force solver for the source problem.

    Returns ``True`` iff there exists an assignment to the variables such that
    *exactly* one literal in each clause is true.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate all 2^m assignments; assignment is a tuple of booleans where
    # index i corresponds to variable i+1.
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_count = sum(bits[v - 1] for v in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance: Dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    Returns ``True`` iff there exists an assignment satisfying all clauses.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit < 0:
                    val = not val
                if val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def random_one_in_three_instance(max_vars: int = 5, max_clauses: int = 4) -> Dict:
    """Generate a random valid instance of ``OneInThreeSat``.

    The function respects the validation constraints: each clause contains
    three *different* positive variable indices between 1 and ``num_vars``.
    """
    # Choose number of variables (allow 0 to test the edge case).
    num_vars = random.randint(0, max_vars)
    # When there are no variables we can only have zero clauses.
    if num_vars < 3:
        clauses: List[List[int]] = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            # pick three distinct variables
            clause = random.sample(range(1, num_vars + 1), 3)
            clauses.append(clause)
    instance = {"num_vars": num_vars, "clauses": clauses}
    # Ensure the generated instance passes validation (it should).
    problems.OneInThreeSat.validate(instance)
    return instance


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    for _ in range(200):  # a reasonable number of random tests
        src = random_one_in_three_instance()
        # Reduce and validate the target instance.
        tgt = reduce_instance(src)
        # Solve both instances.
        src_ans = solve_one_in_three(src)
        tgt_ans = solve_three_sat(tgt)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            # If a mismatch occurs, print details for debugging.
            print("Mismatch!", file=sys.stderr)
            print("Source:", json.dumps(src), file=sys.stderr)
            print("Target:", json.dumps(tgt), file=sys.stderr)
            print("Source answer:", src_ans, "Target answer:", tgt_ans, file=sys.stderr)
    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    # Also print the verdict for visibility.
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

