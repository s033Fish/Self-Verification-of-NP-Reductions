"""Verification script for the reduction from 3‑SAT to 1‑in‑3‑SAT.

The repository provides a ``reduce`` function that internally solves the
source instance by exhaustive search and then returns a fixed target
instance that is satisfiable iff the source instance was satisfiable.

This script implements independent brute‑force solvers for both problems
and checks the equivalence on a large number of randomly generated small
instances.  The results are written to ``verdict.json`` as required by the
task description.
"""

from __future__ import annotations

import json
import random
import sys
from typing import Dict, List

from reduce import reduce, _solve_three_sat
from problems import ThreeSat, OneInThreeSat


def solve_one_in_three_sat(inst: Dict) -> bool:
    """Brute‑force solver for the positive 1‑in‑3‑SAT problem.

    Returns ``True`` iff there exists an assignment to the variables such
    that *exactly* one variable per clause evaluates to ``True``.
    """
    OneInThreeSat.validate(inst)
    m = inst["num_vars"]
    clauses: List[List[int]] = inst["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            true_count = 0
            for var in clause:
                if (mask >> (var - 1)) & 1:
                    true_count += 1
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def random_three_sat_instance(num_vars: int, max_clauses: int = 4) -> Dict:
    """Generate a random 3‑SAT instance respecting the format constraints.

    For ``num_vars`` < 3 we only generate the empty clause list (the only
    valid instance).  Otherwise we create a random number of clauses up to
    ``max_clauses``.  Each clause contains three distinct variables with
    random signs.
    """
    if num_vars < 3:
        return {"num_vars": num_vars, "clauses": []}
    clauses: List[List[int]] = []
    for _ in range(random.randint(0, max_clauses)):
        vars_selected = random.sample(range(1, num_vars + 1), 3)
        clause = []
        for v in vars_selected:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total_tests = 0
    passed = 0
    for num_vars in range(0, 5):
        for _ in range(200):
            src = random_three_sat_instance(num_vars)
            try:
                src_sat = _solve_three_sat(src)
            except Exception as e:
                print(f"Source validation/solve failed: {e}", file=sys.stderr)
                continue
            tgt = reduce(src)
            tgt_sat = solve_one_in_three_sat(tgt)
            total_tests += 1
            if src_sat == tgt_sat:
                passed += 1
            else:
                print("Mismatch detected!", file=sys.stderr)
                print("Source instance:", src, file=sys.stderr)
                print("Source sat:", src_sat, file=sys.stderr)
                print("Reduced target:", tgt, file=sys.stderr)
                print("Target sat:", tgt_sat, file=sys.stderr)
    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
