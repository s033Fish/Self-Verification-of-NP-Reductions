"""Test harness for the SubsetSum → SAT reduction.

The repository provides only validation utilities for the two problems.
This file implements straightforward brute‑force solvers for both
problems and then checks that ``reduce`` produces a SAT instance whose
answer matches the original Subset Sum instance.

The script runs a modest number of random small instances as well as a
hand‑crafted set of edge‑case instances.  It writes a ``verdict.json``
file containing the total number of tests run, how many passed, and a
boolean ``verified`` flag indicating whether all tests succeeded.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict

from problems import SubsetSum, Sat
from reduce import reduce as reduce_instance


def subset_sum_bruteforce(numbers: List[int], target: int) -> bool:
    """Return True iff a sub‑list of *numbers* sums to *target*.

    This follows the exact definition from ``SubsetSum``:
    * The empty sub‑list is allowed.
    * Each position may be used at most once.
    * Numbers are non‑negative, but the algorithm works for any ints.
    """
    # Edge cases according to the problem statement.
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    # Enumerate all subsets via bit masks.
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def sat_bruteforce(num_vars: int, clauses: List[List[int]]) -> bool:
    """Return True iff the CNF formula is satisfiable.

    ``num_vars`` may be zero.  An empty clause (``[]``) is unsatisfiable.
    """
    # If there is an empty clause, the formula is unsatisfiable.
    for clause in clauses:
        if len(clause) == 0:
            return False
    # Enumerate all assignments.
    for assignment in product([False, True], repeat=num_vars):
        # assignment[i] corresponds to variable i+1.
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def run_tests() -> Dict[str, int | bool]:
    total = 0
    passed = 0

    # Hand‑crafted edge cases.
    edge_cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 5},
        {"numbers": [0, 0], "target": 0},
        {"numbers": [1, 2, 3], "target": -1},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 4},
    ]

    for inst in edge_cases:
        total += 1
        try:
            SubsetSum.validate(inst)
        except Exception as e:
            print("Invalid source instance", inst, e, file=sys.stderr)
            continue
        ss_ans = subset_sum_bruteforce(inst["numbers"], inst["target"])
        sat_inst = reduce_instance(inst)
        Sat.validate(sat_inst)
        sat_ans = sat_bruteforce(sat_inst["num_vars"], sat_inst["clauses"])
        if ss_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch on edge case", inst, ss_ans, sat_ans, file=sys.stderr)

    # Random tests.
    random.seed(0)
    for _ in range(200):
        n = random.randint(0, 6)
        numbers = [random.randint(0, 10) for _ in range(n)]
        target = random.randint(-5, 20)
        inst = {"numbers": numbers, "target": target}
        total += 1
        SubsetSum.validate(inst)
        ss_ans = subset_sum_bruteforce(numbers, target)
        sat_inst = reduce_instance(inst)
        Sat.validate(sat_inst)
        sat_ans = sat_bruteforce(sat_inst["num_vars"], sat_inst["clauses"])
        if ss_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch on random instance", inst, ss_ans, sat_ans, file=sys.stderr)

    return {"tests_run": total, "tests_passed": passed, "verified": total == passed}


if __name__ == "__main__":
    result = run_tests()
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    print(json.dumps(result, indent=2))

