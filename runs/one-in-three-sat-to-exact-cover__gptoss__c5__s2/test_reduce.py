"""Automated tests for the reduction from OneInThreeSat to ExactCover.

The repository provides only validators and the reduction implementation.
We implement brute‑force solvers for both source and target problems and
compare the answer of the reduction on a collection of small random
instances.  The tests are deliberately limited to tiny sizes so that the
exponential brute‑force checks finish quickly.

If all generated instances agree, we write ``verdict.json`` with the
verification result.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Dict, Any

from problems import OneInThreeSat, ExactCover
from reduce import reduce as reduce_instance


def solve_one_in_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for the source problem.

    Returns True iff there exists an assignment to the variables such that
    exactly one literal in each clause is true.
    """
    OneInThreeSat.validate(instance)
    num_vars = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for assign in range(1 << num_vars):
        ok = True
        for clause in clauses:
            true_cnt = 0
            for var in clause:
                if (assign >> (var - 1)) & 1:
                    true_cnt += 1
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for Exact Cover.

    Checks all subsets of the given sets (up to 2**len(sets)).  For each
    subset we verify that the chosen sets are pairwise disjoint and their
    union equals the whole universe.
    """
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    # Pre‑compute bitmask representation for speed.
    set_masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        set_masks.append(mask)
    full_mask = (1 << u) - 1
    n_sets = len(sets)
    for choice in range(1 << n_sets):
        combined = 0
        ok = True
        for i in range(n_sets):
            if (choice >> i) & 1:
                if combined & set_masks[i]:
                    ok = False  # overlap
                    break
                combined |= set_masks[i]
        if ok and combined == full_mask:
            return True
    return False


def random_one_in_three_instance(max_vars: int, max_clauses: int) -> Dict[str, Any]:
    """Generate a random valid OneInThreeSat instance.

    Variables are numbered 1..m.  Each clause consists of three distinct
    variables chosen uniformly at random.
    """
    m = random.randint(0, max_vars)
    # Ensure we have at least 3 variables when we generate clauses.
    if m > 0 and m < 3:
        m = 3
    c = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(c):
        if m == 0:
            # No variables – we cannot create a valid clause, so break.
            break
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clauses.append(vars_in_clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        instance = random_one_in_three_instance(max_vars=4, max_clauses=4)
        # Validate the generated instance (should always pass).
        OneInThreeSat.validate(instance)
        src_ans = solve_one_in_three_sat(instance)
        reduced = reduce_instance(instance)
        tgt_ans = solve_exact_cover(reduced)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            # Print the failing case for debugging.
            print("Mismatch!", file=sys.stderr)
            print("Source instance:", json.dumps(instance), file=sys.stderr)
            print("Reduced instance:", json.dumps(reduced), file=sys.stderr)
            print("Source answer:", src_ans, "Target answer:", tgt_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

