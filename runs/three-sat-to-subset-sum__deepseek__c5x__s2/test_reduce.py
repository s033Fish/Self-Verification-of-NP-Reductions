"""Automated tests for the reduction from ThreeSat to SubsetSum.

The repository provides only validation helpers for the two problems.  To
verify the correctness of ``reduce.py`` we implement tiny brute‑force
solvers for both source and target problems and then compare the answers on
many randomly generated instances.

The test runner prints a short summary and exits with a non‑zero status if a
discrepancy is found – this will cause the final verdict JSON to be marked as
``verified: false``.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict, Any

import problems  # provides ThreeSat, SubsetSum validation
from reduce import reduce as reduction


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force SAT solver for the ThreeSat definition.

    Returns ``True`` iff there exists an assignment to the ``num_vars``
    variables that satisfies every clause.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Iterate over all 2^m assignments as tuples of booleans.
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # clause satisfied if any literal evaluates to True under assignment
            lit_ok = False
            for lit in clause:
                var = abs(lit) - 1  # 0‑based index
                val = assignment[var]
                if lit < 0:
                    val = not val
                if val:
                    lit_ok = True
                    break
            if not lit_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for Subset Sum.

    Returns ``True`` if a sub‑list of ``numbers`` sums exactly to ``target``.
    """
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    n = len(numbers)
    # Early exit for trivial cases matching the specification.
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


def random_three_sat(max_vars: int = 4, max_clauses: int = 5) -> Dict[str, Any]:
    """Generate a random, valid ThreeSat instance.

    The generator respects the validation rules: each clause contains three
    distinct variables, no variable appears both positively and negatively in
    the same clause, and literals are non‑zero.
    """
    m = random.randint(0, max_vars)
    # Edge case: if there are no variables, there can be no clauses.
    if m == 0:
        return {"num_vars": 0, "clauses": []}
    # If fewer than 3 variables, cannot create a 3‑literal clause.
    if m < 3:
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # Choose three distinct variables.
        vars_chosen = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_chosen:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic behaviour for reproducibility
    total = 0
    passed = 0
    # Run a reasonable number of random tests.
    for _ in range(200):
        src = random_three_sat()
        # Validate source instance (will raise if malformed).
        problems.ThreeSat.validate(src)
        tgt = reduction(src)
        problems.SubsetSum.validate(tgt)
        ans_src = solve_three_sat(src)
        ans_tgt = solve_subset_sum(tgt)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            # Print a minimal debug dump for the failing case.
            print("Mismatch detected!", file=sys.stderr)
            print("Source instance:", json.dumps(src), file=sys.stderr)
            print("Reduced target:", json.dumps(tgt), file=sys.stderr)
            print("Source answer:", ans_src, "Target answer:", ans_tgt, file=sys.stderr)
            break
    # Write verdict JSON as required by the task.
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)
    # Print a short summary.
    print(f"Tests run: {total}, passed: {passed}, verified: {verdict['verified']}")
    # Exit with non‑zero code if not verified, to make CI aware.
    sys.exit(0 if verdict["verified"] else 1)


if __name__ == "__main__":
    main()
