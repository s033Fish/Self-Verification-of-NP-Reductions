"""Tests for the reduction from OneInThreeSat to ThreeSat.

The file defines brute‑force solvers for the source and target problems
according to the specifications in ``problems.py`` and then exhaustively
generates small instances to verify that ``reduce.py`` produces an
equivalent ThreeSat instance.

The script is executed by the evaluation harness; it prints a JSON object
with the number of tests run and passed.  The final verdict is written to
``verdict.json``.
"""

from __future__ import annotations

import json
import itertools
import sys
from pathlib import Path

# Import problem definitions and the reduction implementation.
import problems
from reduce import reduce as reduce_instance


def solve_one_in_three(instance: dict) -> bool:
    """Brute‑force solver for OneInThreeSat.

    Returns True iff there exists an assignment to the variables that makes
    exactly one literal true in each clause.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Iterate over all 2^m assignments.
    for bits in range(1 << m):
        ok = True
        for a, b, c in clauses:
            # Variables are 1‑based.
            vals = [bool(bits & (1 << (v - 1))) for v in (a, b, c)]
            if sum(vals) != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force solver for ThreeSat.

    Returns True iff there exists an assignment satisfying all clauses.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = bool(bits & (1 << (var - 1)))
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def generate_instances(max_vars: int, max_clauses: int):
    """Yield all well‑formed OneInThreeSat instances up to the given limits.

    The generation respects the validation rules: each clause consists of
    three distinct positive variables in the range 1..m.
    """
    for m in range(0, max_vars + 1):
        # For m < 3 we can only have zero clauses.
        possible_clauses = []
        if m >= 3:
            vars_range = list(range(1, m + 1))
            possible_clauses = list(itertools.combinations(vars_range, 3))
        # Allow repetitions, so we consider product with replacement.
        for num_clauses in range(0, max_clauses + 1):
            if num_clauses == 0:
                yield {"num_vars": m, "clauses": []}
                continue
            for clause_tuple in itertools.product(possible_clauses, repeat=num_clauses):
                clauses = [list(c) for c in clause_tuple]
                yield {"num_vars": m, "clauses": clauses}


def main() -> None:
    total = 0
    passed = 0
    for instance in generate_instances(max_vars=4, max_clauses=2):
        # Validate source instance (may raise InvalidInstance).
        try:
            problems.OneInThreeSat.validate(instance)
        except Exception:
            continue
        total += 1
        src_ans = solve_one_in_three(instance)
        # Apply reduction.
        tgt_instance = reduce_instance(instance)
        # Validate target instance.
        try:
            problems.ThreeSat.validate(tgt_instance)
        except Exception as e:
            print(f"Target instance validation failed: {e}", file=sys.stderr)
            continue
        tgt_ans = solve_three_sat(tgt_instance)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Source instance:", json.dumps(instance), file=sys.stderr)
            print("Reduced instance:", json.dumps(tgt_instance), file=sys.stderr)
            print(f"src_ans={src_ans}, tgt_ans={tgt_ans}", file=sys.stderr)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

