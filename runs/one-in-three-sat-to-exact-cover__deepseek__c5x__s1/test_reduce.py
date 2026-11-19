"""Test the reduction from OneInThreeSat to ExactCover.

The script implements brute‑force solvers for both problems based on the
definitions in ``problems.py``.  It then generates a number of random small
instances of the source problem, applies ``reduce`` and checks that the
answers agree.  The results are written to ``verdict.json`` as required by the
task description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations

from problems import OneInThreeSat, ExactCover
from reduce import reduce as reduce_instance


def solve_one_in_three_sat(instance: dict) -> bool:
    """Brute‑force solver for the positive 1‑in‑3‑SAT problem.

    Returns ``True`` iff there exists an assignment of the variables that makes
    exactly one literal true in each clause.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all 2^m assignments; represent assignment as a tuple of bools
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # clause contains variable indices (1‑based)
            true_count = sum(bits[var - 1] for var in clause)
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """Brute‑force solver for Exact Cover.

    The universe size is small in the generated tests, so we can simply try
    every subset of the given sets.
    """
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    universe = set(range(u))
    # Pre‑convert each set to a Python ``set`` for fast operations.
    set_objs = [set(s) for s in sets]
    # Try all combinations of sets (including the empty combination).
    for r in range(n + 1):
        for combo in combinations(range(n), r):
            covered = set()
            disjoint = True
            for idx in combo:
                s = set_objs[idx]
                if covered & s:
                    disjoint = False
                    break
                covered |= s
            if disjoint and covered == universe:
                return True
    return False


def random_one_in_three_instance(max_vars: int = 5, max_clauses: int = 5) -> dict:
    """Generate a random valid instance of the source problem.

    The generator respects the validation rules: each clause contains three
    distinct positive variables.
    """
    m = random.randint(0, max_vars)
    # Ensure that if we generate any clauses we have at least 3 variables.
    if m < 3:
        # either produce no clauses or increase m to 3
        if random.random() < 0.5:
            return {"num_vars": m, "clauses": []}
        else:
            m = 3
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick three distinct variables from 1..m
        clause = random.sample(range(1, m + 1), 3)
        random.shuffle(clause)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    tests = 200
    passed = 0
    for _ in range(tests):
        src = random_one_in_three_instance()
        # Validate the source instance (will raise on error).
        OneInThreeSat.validate(src)
        # Compute reduction and validate target instance.
        tgt = reduce_instance(src)
        ExactCover.validate(tgt)
        # Solve both.
        ans_src = solve_one_in_three_sat(src)
        ans_tgt = solve_exact_cover(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            # Print a minimal diagnostic for debugging purposes.
            print("Mismatch found:")
            print(json.dumps({"src": src, "tgt": tgt, "src_ans": ans_src, "tgt_ans": ans_tgt}, indent=2))
            break
    verdict = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

