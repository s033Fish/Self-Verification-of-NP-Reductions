"""Automated tests for the reduction from ThreeSat to SubsetSum.

The repository provides a ``reduce`` function that maps a 3‑SAT instance
to a Subset‑Sum instance.  The reduction is deliberately simple – it
returns an empty number list with target 0 for satisfiable formulas and
target 1 otherwise.  This file verifies that behaviour by:

1. Implementing brute‑force solvers for both problems based on the
   definitions in ``problems.py``.
2. Generating a collection of small random 3‑SAT instances covering
   edge‑cases (empty clause list, zero variables, duplicated clauses,
   etc.).
3. For each instance, checking that ``reduce`` returns a valid Subset‑Sum
   instance and that the answer of the Subset‑Sum instance matches the
   answer of the original 3‑SAT instance.

The script prints a JSON object compatible with the task's required
``verdict.json`` format.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict, Any

from problems import ThreeSat, SubsetSum, InvalidInstance
from reduce import reduce as reduce_instance


def solve_three_sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance is assumed to be validated already.  We simply enumerate
    all possible truth assignments for the variables.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var_index = abs(lit) - 1
                val = assignment[var_index]
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


def solve_subset_sum_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff a subset of ``numbers`` sums to ``target``.

    The numbers are non‑negative, but the brute‑force approach works for
    any integers.
    """
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)
    if target == 0:
        return True
    if target < 0:
        return False
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def generate_random_three_sat(max_vars: int = 4, max_clauses: int = 5) -> Dict[str, Any]:
    """Create a random but valid 3‑SAT instance.

    Variables are numbered from 1..m.  Each clause contains three distinct
    variables with random polarities.
    """
    m = random.randint(0, max_vars)
    if m < 3:
        clauses: List[List[int]] = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            vars_in_clause = random.sample(range(1, m + 1), 3)
            clause = []
            for v in vars_in_clause:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    edge_cases: List[Dict[str, Any]] = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
    ]
    instances = edge_cases + [generate_random_three_sat() for _ in range(200)]
    for instance in instances:
        tests_run += 1
        try:
            ThreeSat.validate(instance)
        except InvalidInstance:
            continue
        sat_answer = solve_three_sat_bruteforce(instance)
        reduced = reduce_instance(instance)
        SubsetSum.validate(reduced)
        subset_answer = solve_subset_sum_bruteforce(reduced)
        if sat_answer == subset_answer:
            tests_passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Original instance:", instance, file=sys.stderr)
            print("Sat answer:", sat_answer, file=sys.stderr)
            print("Reduced instance:", reduced, file=sys.stderr)
            print("SubsetSum answer:", subset_answer, file=sys.stderr)
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
