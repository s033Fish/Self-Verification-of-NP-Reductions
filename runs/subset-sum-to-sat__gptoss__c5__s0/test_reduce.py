"""Automated tests for the reduction from Subset Sum to SAT.

The repository provides a ``reduce`` function that converts a Subset Sum
instance to a SAT instance.  To verify its correctness we implement
*brute‑force* solvers for both problems and compare the answers on a
large set of randomly generated small instances.

The test script is deliberately simple – it does not depend on any test
framework.  It prints a short summary and exits with a non‑zero status if
any test fails, which allows the surrounding automation to detect a
problem.
"""

from __future__ import annotations

import random
import sys
from itertools import product, combinations
from typing import List, Dict, Any

from problems import SubsetSum, Sat
from reduce import reduce as reduction


def subset_sum_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the Subset Sum instance is a YES instance.

    The instance follows the format defined in :class:`SubsetSum`.
    """
    SubsetSum.validate(instance)
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]

    # Edge cases from the problem statement
    if target == 0:
        return True
    if target < 0:
        return False
    if not numbers:
        return False

    n = len(numbers)
    # Enumerate all subsets (each position used at most once)
    for r in range(1, n + 1):
        for combo in combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in :class:`Sat`.
    """
    Sat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: a clause list containing an empty clause is unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # No clauses -> trivially satisfiable.
    if not clauses:
        return True

    # Iterate over all possible assignments of m boolean variables.
    for assignment in product([False, True], repeat=m):
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


def generate_random_instance() -> Dict[str, Any]:
    """Generate a small random Subset Sum instance.

    Numbers list length is at most 3 and each number is between 0 and 3.
    Target ranges from -2 to 5.
    """
    length = random.randint(0, 3)
    numbers = [random.randint(0, 3) for _ in range(length)]
    target = random.randint(-2, 5)
    return {"numbers": numbers, "target": target}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 100
    passed = 0
    for i in range(total):
        src = generate_random_instance()
        expected_subset = subset_sum_bruteforce(src)
        sat_instance = reduction(src)
        actual_sat = sat_bruteforce(sat_instance)
        if expected_subset != actual_sat:
            print("FAIL on instance", i)
            print("Source:", src)
            print("Reduced SAT instance:", sat_instance)
            print("Expected SubsetSum answer:", expected_subset)
            print("Actual SAT answer:", actual_sat)
            sys.exit(1)
        passed += 1
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    import json, pathlib
    pathlib.Path("verdict.json").write_text(json.dumps(verdict))
    print(f"All {passed} tests passed.")

if __name__ == "__main__":
    main()
