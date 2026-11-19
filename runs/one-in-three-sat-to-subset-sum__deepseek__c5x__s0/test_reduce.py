"""Test the reduction from OneInThreeSat to SubsetSum.

The test suite implements naïve brute‑force solvers for both problems and
exhaustively checks a large number of small random instances that satisfy the
validation rules defined in ``problems.py``. For each generated source
instance we compute the reduced target instance via ``reduce.reduce`` and
verify that the answers coincide.

If *all* generated instances agree we output a verdict JSON file indicating
that the reduction has been verified.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product

import problems
import reduce


def solve_one_in_three(instance: dict) -> bool:
    """Brute‑force solver for the 1‑in‑3‑SAT problem.

    Returns True iff there exists an assignment of the ``num_vars`` boolean
    variables such that each clause contains exactly one true literal.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all 2^m assignments represented as bit masks
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            true_cnt = 0
            for var in clause:
                if mask & (1 << (var - 1)):
                    true_cnt += 1
                if true_cnt > 1:
                    break
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """Brute‑force solver for Subset Sum.

    ``instance`` contains a list ``numbers`` (non‑negative ints) and an int
    ``target``. Returns True iff some sub‑multiset of ``numbers`` sums to the
    target.
    """
    numbers = instance["numbers"]
    target = instance["target"]
    reachable = {0}
    for num in numbers:
        new_reachable = set(reachable)
        for s in reachable:
            new_reachable.add(s + num)
        reachable = new_reachable
        if target in reachable:
            return True
    return target in reachable


def generate_random_instance(max_vars: int = 4, max_clauses: int = 4) -> dict:
    """Generate a random valid OneInThreeSat instance.

    ``max_vars`` and ``max_clauses`` bound the size of the generated instance.
    The function respects the validation constraints: each clause contains
    three distinct positive literals and variables are numbered from 1.
    If ``num_vars`` is less than 3 we generate an instance with zero clauses.
    """
    m = random.randint(0, max_vars)
    if m < 3:
        n = 0
    else:
        n = random.randint(0, max_clauses)
    clauses = []
    for _ in range(n):
        clause = random.sample(range(1, m + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        src = generate_random_instance()
        try:
            problems.OneInThreeSat.validate(src)
        except Exception as exc:
            print("Invalid generated instance", src, exc, file=sys.stderr)
            continue
        tgt = reduce.reduce(src)
        problems.SubsetSum.validate(tgt)
        ans_src = solve_one_in_three(src)
        ans_tgt = solve_subset_sum(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, tgt, ans_src, ans_tgt, file=sys.stderr)
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

