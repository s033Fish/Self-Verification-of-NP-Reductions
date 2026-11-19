"""Test suite for the SAT → 3‑SAT reduction.

The repository provides only the problem definitions and the reduction
function.  To verify the reduction we implement tiny brute‑force solvers
for SAT and 3‑SAT based directly on the specifications in ``problems.py``.

For a range of small instances we compare the answer of the original SAT
instance with the answer of the reduced 3‑SAT instance.  If all answers
agree the reduction is considered verified.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))  # ensure local imports work

from problems import Sat, ThreeSat
from reduce import reduce as reduce_sat_to_3sat


def sat_solver(instance: dict) -> bool:
    """Brute‑force SAT solver.

    Returns ``True`` iff there exists an assignment satisfying all clauses.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: any empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # Iterate over all 2^m assignments.
    for bits in range(1 << m):
        # assignment[i] is True if variable i+1 is true.
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            # clause satisfied if any literal evaluates to True.
            if not any((literal > 0 and assignment[literal - 1]) or (literal < 0 and not assignment[-literal - 1]) for literal in clause):
                ok = False
                break
        if ok:
            return True
    return False


def three_sat_solver(instance: dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    The format is identical to SAT, only the clauses are guaranteed to have
    exactly three literals on distinct variables.  The evaluation logic is the
    same as ``sat_solver``.
    """
    return sat_solver(instance)


def generate_random_instance(num_vars: int, max_clauses: int = 4) -> dict:
    """Create a random SAT instance.

    Clauses may have any length (including 0) and may contain duplicate or
    contradictory literals – this mirrors the full SAT definition.
    """
    literals = []
    for v in range(1, num_vars + 1):
        literals.extend([v, -v])
    clauses = []
    for _ in range(random.randint(0, max_clauses)):
        length = random.randint(0, max(0, num_vars))  # allow empty clause
        clause = [random.choice(literals) for _ in range(length)]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    # Test deterministic edge cases first.
    edge_cases = [
        {"num_vars": 0, "clauses": []},  # empty formula, satisfiable
        {"num_vars": 2, "clauses": [[]]},  # contains empty clause -> unsat
        {"num_vars": 2, "clauses": [[1, -1]]},  # tautology clause -> sat
    ]
    for inst in edge_cases:
        total += 1
        Sat.validate(inst)
        ThreeSat.validate(reduce_sat_to_3sat(inst))
        original = sat_solver(inst)
        reduced = three_sat_solver(reduce_sat_to_3sat(inst))
        if original == reduced:
            passed += 1
        else:
            print("Mismatch on edge case", inst, original, reduced, file=sys.stderr)

    # Random testing for small numbers of variables.
    for num_vars in range(0, 4):  # 0..3 variables
        for _ in range(30):  # 30 random instances each
            inst = generate_random_instance(num_vars)
            total += 1
            try:
                Sat.validate(inst)
            except Exception as e:
                # Should never happen for generated instances.
                print("Invalid generated instance", inst, e, file=sys.stderr)
                continue
            reduced = reduce_sat_to_3sat(inst)
            try:
                ThreeSat.validate(reduced)
            except Exception as e:
                print("Reduction produced invalid 3‑SAT instance", reduced, e, file=sys.stderr)
                continue
            original = sat_solver(inst)
            reduced_ans = three_sat_solver(reduced)
            if original == reduced_ans:
                passed += 1
            else:
                print("Mismatch", inst, original, reduced, reduced_ans, file=sys.stderr)

    # Write verdict.
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

