"""Test the reduction from OneInThreeSat to SubsetSum.

The script generates many small random instances of the source problem,
applies the reduction, validates the produced target instance, and then
compares the answers of brute‑force solvers for both problems.

The outcome is written to ``verdict.json`` in the repository root.  The
``verified`` flag is true only if every generated test case yields matching
answers.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations

import problems
import reduce


def solve_one_in_three_sat(instance: dict) -> bool:
    """Brute‑force solver for the positive 1‑in‑3‑SAT problem.

    Returns True iff there exists an assignment of ``True``/``False`` to the
    variables ``1..m`` such that each clause has exactly one true literal.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all 2^m assignments represented as bits of an integer
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            # count how many variables in clause are true in this assignment
            true_cnt = sum(((bits >> (var - 1)) & 1) for var in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Brute‑force solver for Subset Sum.

    Returns True iff a subset of ``numbers`` sums exactly to ``target``.
    """
    nums = instance["numbers"]
    target = instance["target"]
    n = len(nums)
    # Simple exhaustive search over all subsets (2^n possibilities).
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += nums[i]
        if s == target:
            return True
    return False


def generate_random_instance() -> dict:
    """Generate a random valid OneInThreeSat instance.

    - ``num_vars`` is chosen between 0 and 5.
    - If ``num_vars`` < 3, the instance will have zero clauses (the only
      valid formula in that regime).
    - Otherwise a random number of clauses (0‑5) is created, each clause
      consisting of three distinct variables.
    """
    m = random.randint(0, 5)
    if m < 3:
        return {"num_vars": m, "clauses": []}
    max_clauses = 5
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic tests
    tests_run = 0
    tests_passed = 0
    mismatches = []

    for _ in range(200):
        src = generate_random_instance()
        # Validate source instance using the library's validator.
        try:
            problems.OneInThreeSat.validate(src)
        except Exception as e:
            print("Generated invalid source instance", src, file=sys.stderr)
            raise

        reduced = reduce.reduce(src)
        # Validate target instance.
        try:
            problems.SubsetSum.validate(reduced)
        except Exception as e:
            print("Reduction produced invalid target instance", reduced, file=sys.stderr)
            raise

        src_ans = solve_one_in_three_sat(src)
        tgt_ans = solve_subset_sum(reduced)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            mismatches.append({"src": src, "reduced": reduced, "src_ans": src_ans, "tgt_ans": tgt_ans})

    verified = tests_run == tests_passed
    verdict = {
        "verified": verified,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    # Write verdict.json
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

    # If there were mismatches, also output them for debugging.
    if not verified:
        with open("mismatches.json", "w", encoding="utf-8") as f:
            json.dump(mismatches, f, indent=2)
        sys.exit(1)

if __name__ == "__main__":
    main()
