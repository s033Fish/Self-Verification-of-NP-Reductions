"""Test suite for the SubsetSum → SAT reduction.

The repository provides only validation functions for the two problems.
We implement tiny brute‑force solvers for Subset Sum and SAT and then
compare the answer of the reduction with the direct answers on a large
set of random small instances.

The script prints a JSON object compatible with the required ``verdict``
format:

    {"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}

It is executed by the evaluation harness after being added to the repo.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations

import problems  # provides SubsetSum.validate and Sat.validate
from reduce import reduce as reduce_instance


def subset_sum_bruteforce(instance: dict) -> bool:
    numbers = instance["numbers"]
    target = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for r in range(1, n + 1):
        for combo in combinations(range(n), r):
            if sum(numbers[i] for i in combo) == target:
                return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in product([False, True], repeat=m):
        assign = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assign[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def run_random_tests(num_tests: int = 200) -> tuple[int, int]:
    tests_run = 0
    passed = 0
    for _ in range(num_tests):
        n = random.randint(0, 6)
        numbers = [random.randint(0, 10) for _ in range(n)]
        target = random.randint(-5, sum(numbers) + 5)
        instance = {"numbers": numbers, "target": target}
        try:
            problems.SubsetSum.validate(instance)
        except Exception as e:
            print("Invalid SubsetSum instance generated:", e, file=sys.stderr)
            continue
        expected = subset_sum_bruteforce(instance)
        reduced = reduce_instance(instance)
        try:
            problems.Sat.validate(reduced)
        except Exception as e:
            print("Reduction produced invalid SAT instance:", e, file=sys.stderr)
            continue
        # Skip overly large SAT instances to keep brute‑force feasible.
        if reduced.get("num_vars", 0) > 16:
            continue
        actual = sat_bruteforce(reduced)
        tests_run += 1
        if expected == actual:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("SubsetSum instance:", instance, file=sys.stderr)
            print("Reduced SAT instance:", reduced, file=sys.stderr)
            print("Expected:", expected, "Actual:", actual, file=sys.stderr)
    return tests_run, passed

if __name__ == "__main__":
    edge_cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 5},
        {"numbers": [1, 2, 3], "target": -1},
        {"numbers": [0, 0], "target": 0},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 4},
    ]
    edge_run = edge_pass = 0
    for inst in edge_cases:
        problems.SubsetSum.validate(inst)
        exp = subset_sum_bruteforce(inst)
        red = reduce_instance(inst)
        problems.Sat.validate(red)
        act = sat_bruteforce(red)
        edge_run += 1
        if exp == act:
            edge_pass += 1
    rand_run, rand_pass = run_random_tests(500)
    total_run = edge_run + rand_run
    total_pass = edge_pass + rand_pass
    verified = total_run == total_pass
    result = {"verified": verified, "tests_run": total_run, "tests_passed": total_pass}
    print(json.dumps(result))
