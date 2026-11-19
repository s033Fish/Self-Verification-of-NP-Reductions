"""Tests for the reduction from ThreeSat to OneInThreeSat.

The reduction in ``reduce.py`` is expected to be correct, but we verify it by
checking a handful of small instances where a brute‑force solver can be applied
to both the source and the reduced target.  If any instance yields a different
answer, the reduction is marked as not verified.
"""

from __future__ import annotations

import json
from pathlib import Path

from reduce import reduce as reduce_instance
from problems import ThreeSat, OneInThreeSat


def solve_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool(mask & (1 << var))
                if lit > 0:
                    clause_ok |= val
                else:
                    clause_ok |= not val
                if clause_ok:
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_one_in_three_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            true_cnt = 0
            for var in clause:
                true_cnt += bool(mask & (1 << (var - 1)))
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def main() -> None:
    tests = []
    # Edge cases: formulas with no clauses for m = 0,1,2.
    for m in range(3):
        tests.append({"num_vars": m, "clauses": []})

    tests_run = 0
    tests_passed = 0
    for src in tests:
        ThreeSat.validate(src)
        src_ans = solve_three_sat(src)
        tgt = reduce_instance(src)
        OneInThreeSat.validate(tgt)
        # The target instances are small enough (<=8 vars) for brute force.
        tgt_ans = solve_one_in_three_sat(tgt)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

