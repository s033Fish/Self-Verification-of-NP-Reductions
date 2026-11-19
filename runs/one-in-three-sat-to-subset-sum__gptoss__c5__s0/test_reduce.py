"""Automated tests for the reduction from 1-in-3 SAT to Subset Sum.

The repository provides only validation functions for the two problems and
the reduction implementation.  To verify the reduction we implement brute-
force solvers for both source and target problems and compare their answers
on a collection of randomly generated small instances.

The script records how many tests were executed and how many passed, then
writes a ``verdict.json`` file as required by the task description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import Dict, List

import problems  # provides validation classes
from reduce import reduce as reduce_instance


def solve_one_in_three_sat(instance: Dict) -> bool:
    """Brute-force solver for the positive 1-in-3 SAT problem.

    The instance format is ``{"num_vars": m, "clauses": [[a, b, c], ...]}``.
    We iterate over all 2^m assignments and check the exactly-one-true
    condition for each clause.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            true_cnt = 0
            for var in clause:
                if mask & (1 << (var - 1)):
                    true_cnt += 1
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: Dict) -> bool:
    """Brute-force solver for Subset Sum.

    ``instance`` has keys ``numbers`` (list of non-negative ints) and
    ``target`` (int).  We try all subsets via bit masks.
    """
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
                if target >= 0 and s > target:
                    break
        if s == target:
            return True
    return False


def random_instance(max_vars: int = 5, max_clauses: int = 4) -> Dict:
    """Generate a random valid instance of the source problem.

    ``max_vars`` and ``max_clauses`` bound the size to keep the brute-force
    solver tractable.
    """
    m = random.randint(0, max_vars)
    if m < 3:
        clauses: List[List[int]] = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            clause = random.sample(range(1, m + 1), 3)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total_tests = 0
    passed = 0
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4]]},
    ]
    instances = edge_cases + [random_instance() for _ in range(200)]
    for inst in instances:
        total_tests += 1
        try:
            problems.OneInThreeSat.validate(inst)
        except Exception as e:
            print(f"Invalid source instance generated: {inst}\n{e}", file=sys.stderr)
            continue
        src_answer = solve_one_in_three_sat(inst)
        red = reduce_instance(inst)
        try:
            problems.SubsetSum.validate(red)
        except Exception as e:
            print(f"Reduction produced invalid target: {red}\n{e}", file=sys.stderr)
            continue
        tgt_answer = solve_subset_sum(red)
        if src_answer == tgt_answer:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print("Source instance:", inst, file=sys.stderr)
            print("Source answer:", src_answer, file=sys.stderr)
            print("Reduced target:", red, file=sys.stderr)
            print("Target answer:", tgt_answer, file=sys.stderr)
    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
