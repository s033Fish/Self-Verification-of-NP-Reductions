"""Tests for the reduction from ThreeSat to SubsetSum.

The file implements brute‑force solvers for the source (ThreeSat) and the
target (SubsetSum) problems, generates a number of small random instances,
applies the provided ``reduce`` function and checks that the answers agree.

The script prints a JSON object compatible with the required ``verdict.json``
format.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict

from problems import ThreeSat, SubsetSum
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict) -> bool:
    """Brute‑force solver for ThreeSat.

    Returns ``True`` iff there exists an assignment satisfying all clauses.
    """
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # iterate over all 2^m assignments (True/False for each variable 1..m)
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1  # zero‑based index
                val = assignment[var]
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


def solve_subset_sum(instance: Dict) -> bool:
    """Brute‑force solver for SubsetSum.

    Returns ``True`` iff some sub‑list of ``numbers`` sums exactly to ``target``.
    """
    SubsetSum.validate(instance)
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)
    # Simple subset enumeration – sufficient for the tiny instances we generate.
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def random_three_sat(max_vars: int = 4, max_clauses: int = 4) -> Dict:
    """Generate a random well‑formed ThreeSat instance.

    The generator respects the constraints of the problem definition:
    * each clause has exactly three literals on three distinct variables
    * a clause never contains both a variable and its negation
    """
    m = random.randint(0, max_vars)
    # Allow zero clauses as a valid edge case.
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # Need at least three distinct variables to form a clause.
        if m < 3:
            break
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        src = random_three_sat()
        ThreeSat.validate(src)
        tgt = reduce_instance(src)
        ans_src = solve_three_sat(src)
        ans_tgt = solve_subset_sum(tgt)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Counterexample found:", json.dumps({"src": src, "tgt": tgt, "ans_src": ans_src, "ans_tgt": ans_tgt}), file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
