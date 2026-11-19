"""Tests for the reduction from ThreeSat to NaeThreeSat.

The file implements brute‑force solvers for both problems based directly on
the definitions in ``problems.py``.  It then enumerates a collection of small
random instances of 3‑SAT, applies the provided ``reduce`` function and checks
that the answer of the original instance matches the answer of the reduced
instance.

If all checks pass the script prints a JSON object suitable for the required
``verdict.json`` file.
"""

from __future__ import annotations

import json
import random
import itertools
from typing import List, Dict, Any

import problems
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for 3‑SAT.

    Returns True iff there exists an assignment to the variables that makes
    every clause contain at least one true literal.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_val = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit < 0:
                    val = not val
                if val:
                    clause_val = True
                    break
            if not clause_val:
                ok = False
                break
        if ok:
            return True
    return False


def solve_nae_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for NAE‑3‑SAT.

    Returns True iff there exists an assignment such that each clause has at
    least one true literal and at least one false literal.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit < 0:
                    val = not val
                vals.append(val)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def generate_random_three_sat_instance(m: int, max_clauses: int) -> Dict[str, Any]:
    """Generate a random valid 3‑SAT instance.

    The instance respects the validation rules in ``problems.py``.
    """
    if m == 0:
        return {"num_vars": 0, "clauses": []}
    clauses: List[List[int]] = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if m < 3:
            break
        vars_selected = random.sample(range(1, m + 1), 3)
        clause = [v if random.choice([True, False]) else -v for v in vars_selected]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total_tests = 0
    passed = 0
    for m in range(0, 5):
        for _ in range(50):
            instance = generate_random_three_sat_instance(m, max_clauses=5)
            problems.ThreeSat.validate(instance)
            reduced = reduce_instance(instance)
            problems.NaeThreeSat.validate(reduced)
            ans_src = solve_three_sat(instance)
            ans_tgt = solve_nae_three_sat(reduced)
            total_tests += 1
            if ans_src == ans_tgt:
                passed += 1
            else:
                print("FAILURE", json.dumps({"src": instance, "tgt": reduced}))
    verdict = {"verified": passed == total_tests, "tests_run": total_tests, "tests_passed": passed}
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
