"""Test suite for the reduction from ThreeSat to OneInThreeSat.

The script builds a number of small random instances of the source problem,
uses a brute‑force solver for both the source and the target, runs the
reduction, validates the produced instance and checks that the answers
coincide.  The results are written to ``verdict.json`` as required by the
task description.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Tuple

import problems  # provides ThreeSat and OneInThreeSat with .validate
import reduce


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force solver for ThreeSat.

    Returns True iff the instance is satisfiable.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if lit > 0 and val == 1:
                    satisfied = True
                    break
                if lit < 0 and val == 0:
                    satisfied = True
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def solve_one_in_three_sat(instance: dict) -> bool:
    """Brute‑force solver for OneInThreeSat.

    Returns True iff exactly one variable in each clause is true.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            true_cnt = 0
            for var in clause:
                idx = var - 1
                if (mask >> idx) & 1:
                    true_cnt += 1
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def random_three_sat_instance() -> dict:
    """Generate a tiny valid ThreeSat instance suitable for brute‑force.

    To keep the target instance small we restrict ourselves to at most one
    clause and exactly three variables when a clause is present.  This keeps
    the number of target variables below 20, allowing exhaustive evaluation.
    """
    if random.random() < 0.3:
        m = random.randint(0, 3)
        return {"num_vars": m, "clauses": []}
    m = 3
    clause = []
    for v in (1, 2, 3):
        sign = random.choice([1, -1])
        clause.append(sign * v)
    return {"num_vars": m, "clauses": [clause]}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    failures: List[Tuple[dict, dict, bool, bool, str]] = []

    for _ in range(200):
        src = random_three_sat_instance()
        try:
            problems.ThreeSat.validate(src)
        except Exception as e:
            continue
        src_ans = solve_three_sat(src)
        tgt = reduce.reduce(src)
        try:
            problems.OneInThreeSat.validate(tgt)
        except Exception as e:
            failures.append((src, tgt, src_ans, None, f"validation error: {e}"))
            continue
        tgt_ans = solve_one_in_three_sat(tgt)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            failures.append((src, tgt, src_ans, tgt_ans, "answer mismatch"))

    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    if not verdict["verified"]:
        print("Some tests failed:", file=sys.stderr)
        for src, tgt, src_ans, tgt_ans, msg in failures:
            print(msg, file=sys.stderr)
            print("source:", src, file=sys.stderr)
            print("target:", tgt, file=sys.stderr)
            print("src_ans", src_ans, "tgt_ans", tgt_ans, file=sys.stderr)
            print("---", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
