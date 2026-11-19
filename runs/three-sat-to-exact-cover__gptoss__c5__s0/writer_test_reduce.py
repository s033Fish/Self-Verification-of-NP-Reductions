"""Tests for the reduction from ThreeSat to ExactCover.

The tests enumerate all small 3‑SAT instances (up to 3 variables and up to 3
clauses) and check that the reduction preserves the answer.
"""
import itertools
import json
from typing import List, Dict, Any

from problems import ThreeSat, ExactCover
from reduce import reduce
from solve_three_sat import solve_three_sat
from solve_exact_cover import solve_exact_cover


def all_clauses(m: int) -> List[List[int]]:
    """Return all possible 3‑literal clauses over variables 1..m.
    Each clause uses three distinct variables and does not contain both a
    variable and its negation.
    """
    literals = []
    vars = list(range(1, m + 1))
    for combo in itertools.combinations(vars, 3):
        # For each variable choose sign +/-
        for signs in itertools.product([1, -1], repeat=3):
            clause = [signs[i] * combo[i] for i in range(3)]
            literals.append(clause)
    return literals


def generate_instances(max_vars: int = 3, max_clauses: int = 3) -> List[Dict[str, Any]]:
    instances = []
    for m in range(max_vars + 1):
        if m < 3:
            # No valid clauses, only the empty formula is allowed.
            instances.append({"num_vars": m, "clauses": []})
            continue
        clauses = all_clauses(m)
        # consider subsets of clauses up to max_clauses
        for r in range(max_clauses + 1):
            for subset in itertools.combinations(clauses, r):
                instances.append({"num_vars": m, "clauses": [list(c) for c in subset]})
    return instances


def main() -> None:
    instances = generate_instances()
    total = len(instances)
    passed = 0
    for inst in instances:
        # validate source
        ThreeSat.validate(inst)
        sat = solve_three_sat(inst)
        red = reduce(inst)
        # validate target
        ExactCover.validate(red)
        ec = solve_exact_cover(red)
        if sat == ec:
            passed += 1
        else:
            print("Mismatch!", inst, "sat", sat, "ec", ec, "reduction", red)
            break
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    main()
