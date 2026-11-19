import json
import random
import sys
from pathlib import Path

import problems
import reduce
import three_sat_solver
import three_color_solver


def generate_instance(max_vars=3, max_clauses=2) -> dict:
    """Generate a small random 3‑SAT instance.

    The sizes are deliberately tiny so that the brute‑force 3‑coloring
    solver finishes quickly.  ``max_vars`` is limited to 3 and the number of
    clauses to 2, which keeps the resulting graph to at most 12 vertices
    (3 base + 2*m + 3*clauses).  This is comfortably searchable by
    exhaustive enumeration.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m < 3:
            continue
        vars_choice = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_choice:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        src = generate_instance()
        try:
            problems.SOURCE.validate(src)
        except Exception:
            continue
        src_ans = three_sat_solver.solve(src)
        tgt = reduce.reduce(src)
        try:
            problems.TARGET.validate(tgt)
        except Exception as e:
            print("Target validation failed", e, file=sys.stderr)
            sys.exit(1)
        tgt_ans = three_color_solver.solve(tgt)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, src_ans, tgt, tgt_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path('verdict.json').write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    sys.exit(0 if verdict["verified"] else 1)

if __name__ == '__main__':
    main()
