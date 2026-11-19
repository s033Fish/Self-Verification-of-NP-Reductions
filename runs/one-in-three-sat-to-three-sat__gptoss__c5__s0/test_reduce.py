"""Test suite for the reduction from OneInThreeSat to ThreeSat.

The script implements brute‑force solvers for both problems based on the
formal definitions in ``problems.py``.  It then generates a number of random
instances of the source problem, applies ``reduce`` and checks that the
answers agree.

The script is deliberately lightweight – it does not depend on any test
framework – because the execution environment for the review task may not have
``pytest`` installed.  At the end it prints two numbers on stdout:

    <tests_run> <tests_passed>

These values are later used to create ``verdict.json``.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Dict, Any

from problems import OneInThreeSat, ThreeSat
from reduce import reduce


def solve_one_in_three(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for OneInThreeSat.

    Returns True iff there exists an assignment of the variables (1..m) such
    that exactly one literal in each clause is true.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # iterate over all 2^m assignments
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            true_cnt = 0
            for var in clause:
                # var is 1‑based; check corresponding bit
                if mask & (1 << (var - 1)):
                    true_cnt += 1
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for ThreeSat.

    Returns True iff there exists an assignment satisfying every 3‑CNF clause.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = bool(mask & (1 << (var - 1)))
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def random_one_in_three_instance(max_vars: int, max_clauses: int) -> Dict[str, Any]:
    """Generate a random valid OneInThreeSat instance.

    Variables are numbered from 1..m.  Each clause consists of three distinct
    positive variables.
    """
    m = random.randint(0, max_vars)
    # Ensure at least 3 variables if we are going to generate any clause
    if m > 0 and m < 3:
        m = 3
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        if m == 0:
            break
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total_tests = 0
    passed = 0

    # Test a mixture of random instances and some hand‑crafted edge cases.
    test_instances: List[Dict[str, Any]] = []
    # Edge cases
    test_instances.append({"num_vars": 0, "clauses": []})
    test_instances.append({"num_vars": 3, "clauses": []})
    test_instances.append({"num_vars": 3, "clauses": [[1, 2, 3]]})
    test_instances.append({"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]})
    # Random instances
    for _ in range(200):
        test_instances.append(random_one_in_three_instance(5, 5))

    for instance in test_instances:
        total_tests += 1
        # Validate source instance (will raise if malformed)
        OneInThreeSat.validate(instance)
        src_ans = solve_one_in_three(instance)
        reduced = reduce(instance)
        # Validate reduced instance
        ThreeSat.validate(reduced)
        tgt_ans = solve_three_sat(reduced)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("FAILURE", json.dumps({"instance": instance, "reduced": reduced, "src_ans": src_ans, "tgt_ans": tgt_ans}), file=sys.stderr)

    # Output the counts in a simple format for the outer script.
    print(total_tests, passed)

if __name__ == "__main__":
    main()
