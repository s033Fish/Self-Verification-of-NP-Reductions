"""Tests for the SubsetSum → SAT reduction.

The repository provides only validation functions for the two problems and a
`reduce` implementation.  To check correctness we implement simple brute‑force
solvers for both problems and compare the answer on many randomly generated
instances (including edge cases).

If the reduction is correct, the SAT instance produced by `reduce` must be
sat/unsat exactly when the original Subset Sum instance is yes/no.
"""

from __future__ import annotations

import random
import json
import sys
from pathlib import Path

import problems
from reduce import reduce as reduce_instance


def subset_sum_brute(instance: dict) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False


def sat_brute(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if not clause:
            return False
    if not clauses:
        return True
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if lit > 0 and val == 1:
                    clause_sat = True
                    break
                if lit < 0 and val == 0:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def run_random_tests(num_tests: int = 200) -> tuple[int, int]:
    tests_run = 0
    passed = 0
    for _ in range(num_tests):
        # Keep the SAT instance tiny for brute force.
        n = random.randint(0, 2)
        numbers = [random.randint(0, 2) for _ in range(n)]
        total = sum(numbers)
        target = random.randint(-3, total + 3)
        instance = {"numbers": numbers, "target": target}
        problems.SubsetSum.validate(instance)
        expected = subset_sum_brute(instance)
        sat_instance = reduce_instance(instance)
        problems.Sat.validate(sat_instance)
        got = sat_brute(sat_instance)
        tests_run += 1
        if expected == got:
            passed += 1
        else:
            print("FAILURE", file=sys.stderr)
            print("SubsetSum instance:", instance, file=sys.stderr)
            print("Expected:", expected, "Got:", got, file=sys.stderr)
            print("Reduced SAT instance:", sat_instance, file=sys.stderr)
    return tests_run, passed

if __name__ == "__main__":
    random.seed(0)
    tests_run, tests_passed = run_random_tests(500)
    verified = tests_run == tests_passed
    verdict = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
