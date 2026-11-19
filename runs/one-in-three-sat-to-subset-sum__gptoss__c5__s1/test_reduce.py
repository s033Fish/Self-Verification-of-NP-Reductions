"""Automated tests for the reduction from OneInThreeSat to SubsetSum.

The script implements brute‑force solvers for both source and target
problems, generates a variety of small random instances, reduces them
using ``reduce.py`` and checks that the answers agree.

The outcome is written to ``verdict.json`` as required by the task.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict

# Import the problem definitions and the reduction implementation.
from problems import OneInThreeSat, SubsetSum
from reduce import reduce as reduce_instance


def solve_one_in_three_sat(instance: Dict) -> bool:
    """Brute‑force solver for OneInThreeSat.

    Returns True iff there exists an assignment of the variables that makes
    exactly one literal true in each clause.
    """
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate all 2^m assignments as booleans in a tuple.
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # Variables are 1‑based.
            true_count = sum(assignment[var - 1] for var in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: Dict) -> bool:
    """Brute‑force solver for SubsetSum using DP (suitable for small inputs)."""
    SubsetSum.validate(instance)
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    # Quick edge cases
    if target == 0:
        return True
    if target < 0:
        return False
    # DP set of reachable sums.
    reachable = {0}
    for num in numbers:
        new_reachable = set(reachable)
        for s in reachable:
            ns = s + num
            if ns == target:
                return True
            if ns < target:
                new_reachable.add(ns)
        reachable = new_reachable
    return target in reachable


def random_instance(max_vars: int = 5, max_clauses: int = 5) -> Dict:
    """Generate a random valid OneInThreeSat instance.

    The number of variables is chosen uniformly from 0..max_vars.  The number
    of clauses is chosen uniformly from 0..max_clauses.  Each clause consists
    of three distinct variables sampled without replacement from the variable
    range (if there are fewer than three variables we simply generate no
    clauses, matching the edge‑case semantics of the problem).
    """
    m = random.randint(0, max_vars)
    if m < 3:
        # According to the spec, formulas with clauses require m >= 3.
        # To stay safe we generate zero clauses when m < 3.
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    tests_run = 0
    tests_passed = 0
    # Include some deterministic edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
    ]
    for instance in edge_cases:
        tests_run += 1
        source_ans = solve_one_in_three_sat(instance)
        reduced = reduce_instance(instance)
        target_ans = solve_subset_sum(reduced)
        if source_ans == target_ans:
            tests_passed += 1
        else:
            print("Mismatch on edge case:", instance, file=sys.stderr)

    # Random tests
    for _ in range(200):
        instance = random_instance()
        tests_run += 1
        try:
            source_ans = solve_one_in_three_sat(instance)
            reduced = reduce_instance(instance)
            target_ans = solve_subset_sum(reduced)
        except Exception as e:
            print("Exception during test", instance, e, file=sys.stderr)
            continue
        if source_ans == target_ans:
            tests_passed += 1
        else:
            print("Mismatch on instance:", instance, file=sys.stderr)

    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
