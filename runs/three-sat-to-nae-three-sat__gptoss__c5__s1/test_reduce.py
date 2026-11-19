"""Automated tests for the reduction from 3‑SAT to NAE‑3‑SAT.

The repository provides a ``reduce`` function together with two private
brute‑force solvers (``_solve_3sat`` and ``_solve_naesat``).  This test suite
exhaustively enumerates small 3‑SAT instances, applies the reduction and checks
that the answer of the original instance matches the answer of the produced
NAE‑3‑SAT instance.

Only tiny instances are generated (up to 4 variables and at most three
clauses) so that the exhaustive search performed by the solvers finishes
quickly.  The test counts how many instances were examined and how many passed.
A JSON verdict file is written at the end of the run.
"""

from __future__ import annotations

import itertools
import json
import os
import sys
from typing import List, Dict

# Import the functions from the reduction module.
from reduce import _solve_3sat, _solve_naesat, reduce


def generate_all_clauses(num_vars: int) -> List[List[int]]:
    """Return a list of all possible 3‑literal clauses over ``num_vars`` variables.

    Each clause contains three distinct variables, each possibly negated.
    Literals are encoded as integers: positive for true, negative for false.
    """
    clauses: List[List[int]] = []
    for vars_combo in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clause = [signs[i] * vars_combo[i] for i in range(3)]
            clauses.append(clause)
    return clauses


def generate_instances(max_vars: int = 4, max_clauses: int = 3) -> List[Dict]:
    """Generate a list of small 3‑SAT instances.

    For each number of variables ``m`` from 0 to ``max_vars`` we consider all
    subsets of the universe of possible clauses up to ``max_clauses`` in size.
    The empty clause list (the trivially satisfiable formula) is also included.
    """
    instances: List[Dict] = []
    for m in range(max_vars + 1):
        possible_clauses = generate_all_clauses(m) if m >= 3 else []
        # Always include the empty formula.
        instances.append({"num_vars": m, "clauses": []})
        for r in range(1, min(max_clauses, len(possible_clauses)) + 1):
            for subset in itertools.combinations(possible_clauses, r):
                instances.append({"num_vars": m, "clauses": [list(c) for c in subset]})
    return instances


def main() -> None:
    # Static analysis: ensure the reduction does not call the brute‑force solver.
    with open(os.path.join(os.getcwd(), "reduce.py"), "r", encoding="utf-8") as f:
        reduce_src = f.read()
    uses_bruteforce = "_solve_3sat(" in reduce_src

    instances = generate_instances()
    total = len(instances)
    passed = 0

    for idx, instance in enumerate(instances, 1):
        expected = _solve_3sat(instance)
        reduced = reduce(instance)
        got = _solve_naesat(reduced)
        if expected == got:
            passed += 1
        else:
            print(f"Mismatch on instance {idx}/{total}: {instance}")
            print(f"  expected (3‑SAT) = {expected}, got (NAE) = {got}")
            print(f"  reduced instance = {reduced}")

    verified = (passed == total) and (not uses_bruteforce)
    verdict = {
        "verified": verified,
        "tests_run": total,
        "tests_passed": passed,
        "uses_bruteforce": uses_bruteforce,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    main()
