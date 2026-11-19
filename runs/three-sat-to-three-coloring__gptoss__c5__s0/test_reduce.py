"""Automated tests for the reduction from 3‑SAT to 3‑Coloring.

The test suite implements brute‑force solvers for both source and target
problems, generates a collection of small random 3‑SAT instances, applies
the provided ``reduce`` function and checks that the answers agree.

If all generated instances behave correctly a ``verdict.json`` file is
written with ``verified: true``; otherwise ``verified`` is ``false`` and
the counts of total and passed tests are recorded.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Dict, List

from problems import ThreeSat, ThreeColoring
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict) -> bool:
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_coloring(instance: Dict) -> bool:
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    for mask in range(3 ** n):
        colours = []
        tmp = mask
        for _ in range(n):
            colours.append(tmp % 3)
            tmp //= 3
        valid = True
        for u, v in edges:
            if colours[u] == colours[v]:
                valid = False
                break
        if valid:
            return True
    return False


def random_three_sat_instance(max_vars: int = 3, max_clauses: int = 2) -> Dict:
    m = random.randint(0, max_vars)
    if m == 0:
        return {"num_vars": 0, "clauses": []}
    if m < 3:
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        vars_selected = random.sample(range(1, m + 1), 3)
        clause = []
        for var in vars_selected:
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    failures: List[Dict] = []
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3]]},
    ]
    for inst in edge_cases:
        total += 1
        try:
            ThreeSat.validate(inst)
        except Exception as e:
            print("Invalid edge case instance:", inst, e)
            continue
        sat = solve_three_sat(inst)
        reduced = reduce_instance(inst)
        col = solve_three_coloring(reduced)
        if sat == col:
            passed += 1
        else:
            failures.append({"instance": inst, "sat": sat, "col": col})

    for _ in range(200):
        inst = random_three_sat_instance()
        total += 1
        try:
            ThreeSat.validate(inst)
        except Exception:
            continue
        sat = solve_three_sat(inst)
        reduced = reduce_instance(inst)
        if reduced["n"] > 10:
            total -= 1
            continue
        col = solve_three_coloring(reduced)
        if sat == col:
            passed += 1
        else:
            failures.append({"instance": inst, "sat": sat, "col": col})

    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    if failures:
        print("\nFailures (showing up to 5):", file=sys.stderr)
        for f in failures[:5]:
            print(json.dumps(f, indent=2), file=sys.stderr)

if __name__ == "__main__":
    main()
