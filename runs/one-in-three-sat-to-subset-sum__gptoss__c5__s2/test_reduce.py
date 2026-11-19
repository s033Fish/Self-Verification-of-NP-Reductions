"""Automated tests for the reduction from OneInThreeSat to SubsetSum.

The repository provides only validation functions.  This test module
implements tiny brute‑force solvers for both source and target problems
and then checks that ``reduce.reduce`` preserves the answer on a large
set of randomly generated instances.

The script is deliberately simple – it runs without any external
dependencies and only uses the standard library.  It prints a short
summary and writes ``verdict.json`` in the repository root.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from pathlib import Path

from problems import OneInThreeSat, SubsetSum
from reduce import reduce as reduction


def solve_one_in_three_sat(instance: dict) -> bool:
    """Brute‑force solver for the positive 1‑in‑3 SAT problem.

    The instance follows the format defined in :class:`OneInThreeSat`.
    """
    m = instance["num_vars"]
    clauses: list[list[int]] = instance["clauses"]
    # Enumerate all 2^m assignments as booleans (True = variable is true).
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # Count how many literals are true in this clause.
            true_cnt = sum(assignment[var - 1] for var in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Brute‑force solver for Subset Sum.

    Uses simple enumeration; suitable for the tiny instances generated
    in the tests (at most 12 numbers).
    """
    numbers: list[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)
    # Early trivial cases.
    if target == 0:
        return True
    if target < 0:
        return False
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return True
    return False


def random_one_in_three_instance(max_vars: int, max_clauses: int) -> dict:
    """Generate a random valid OneInThreeSat instance.

    * ``max_vars`` – upper bound for the number of variables (inclusive).
    * ``max_clauses`` – upper bound for the number of clauses.
    """
    m = random.randint(0, max_vars)
    # Number of clauses can be zero.
    k = random.randint(0, max_clauses)
    clauses = []
    for _ in range(k):
        # Choose three distinct variables from 1..m. If m < 3 we cannot
        # create a clause, so we break early.
        if m < 3:
            break
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    # Generate a reasonable number of tests covering edge cases.
    for _ in range(200):
        inst = random_one_in_three_instance(max_vars=5, max_clauses=5)
        # Validate source instance (will raise if invalid).
        OneInThreeSat.validate(inst)
        # Compute answers.
        src_ans = solve_one_in_three_sat(inst)
        red_inst = reduction(inst)
        tgt_ans = solve_subset_sum(red_inst)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Source instance:", json.dumps(inst), file=sys.stderr)
            print("Reduced instance:", json.dumps(red_inst), file=sys.stderr)
            print(f"src_ans={src_ans}, tgt_ans={tgt_ans}", file=sys.stderr)
            break
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
