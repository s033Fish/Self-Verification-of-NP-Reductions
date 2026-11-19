"""Test harness for the SubsetSum → SAT reduction.

The repository provides a ``reduce`` function that maps a Subset Sum instance
to a SAT instance.  The task is to verify that the reduction is correct: for
every (small) Subset Sum instance the answer to the original problem must be
identical to the answer of the produced SAT instance.

Because the original repository does not contain solvers, we implement tiny
brute‑force solvers for both problems.  They are exponential but fast enough
for the tiny instances used in the test suite.

The script generates a number of random instances, runs the reduction, solves
both the original and the reduced instance, and records the results.  Finally
it writes ``verdict.json`` with the required fields.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict, Any

from problems import SubsetSum, Sat
from reduce import reduce as reduce_instance


def subset_sum_bruteforce(instance: Dict[str, Any]) -> bool:
    SubsetSum.validate(instance)
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    Sat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for assignment in product([False, True], repeat=m):
        ok = True
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
                ok = False
                break
        if ok:
            return True
    return False


def generate_random_instance(max_len: int = 3, max_val: int = 1) -> Dict[str, Any]:
    length = random.randint(0, max_len)
    numbers = [random.randint(0, max_val) for _ in range(length)]
    total = sum(numbers)
    target = random.randint(-2, total + 2)
    return {"numbers": numbers, "target": target}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    for _ in range(50):
        instance = generate_random_instance()
        expected = subset_sum_bruteforce(instance)
        reduced = reduce_instance(instance)
        actual = sat_bruteforce(reduced)
        tests_run += 1
        if expected == actual:
            tests_passed += 1
        else:
            print("Mismatch detected:")
            print("SubsetSum instance:", instance)
            print("Expected (SubsetSum):", expected)
            print("Reduced SAT instance:", reduced)
            print("Actual (SAT):", actual)
            sys.stdout.flush()
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
