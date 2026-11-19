"""Automated tests for the reduction from NAE-3-SAT to 3-Coloring.

The script enumerates all small NAE-3-SAT instances, solves them by brute
force, reduces them using ``reduce.reduce`` and solves the resulting graph
by brute force as well.  If the answers differ, the reduction is incorrect.

The script writes a ``verdict.json`` file with the fields required by the
task description.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce as reduce_instance


def solve_nae3sat(instance: dict) -> bool:
    """Brute‑force solver for NAE‑3‑SAT.

    Returns ``True`` iff there exists an assignment of ``num_vars`` boolean
    variables satisfying the not‑all‑equal condition for every clause.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                var_val = (mask >> var) & 1
                lit_val = var_val if lit > 0 else (1 - var_val)
                vals.append(lit_val)
            if all(v == 1 for v in vals) or all(v == 0 for v in vals):
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_coloring(instance: dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns ``True`` iff the graph can be coloured with three colours
    (0,1,2) such that adjacent vertices receive different colours.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    for num in range(3 ** n):
        colours = []
        tmp = num
        for _ in range(n):
            colours.append(tmp % 3)
            tmp //= 3
        good = True
        for u, v in edges:
            if colours[u] == colours[v]:
                good = False
                break
        if good:
            return True
    return False


def generate_all_instances(max_vars: int = 3, max_clauses: int = 2) -> list[dict]:
    """Generate every NAE‑3‑SAT instance within the given limits.

    * ``max_vars`` – maximum number of variables (inclusive).
    * ``max_clauses`` – maximum number of clauses (inclusive).
    """
    instances = []
    for m in range(0, max_vars + 1):
        clause_set = []
        if m >= 3:
            for combo in itertools.combinations(range(1, m + 1), 3):
                for signs in itertools.product([1, -1], repeat=3):
                    clause = [signs[i] * combo[i] for i in range(3)]
                    clause_set.append(clause)
        for c_len in range(0, max_clauses + 1):
            if c_len == 0:
                instances.append({"num_vars": m, "clauses": []})
                continue
            if not clause_set:
                continue
            for clause_list in itertools.product(clause_set, repeat=c_len):
                instances.append({"num_vars": m, "clauses": [list(cl) for cl in clause_list]})
    return instances


def main() -> None:
    instances = generate_all_instances(max_vars=3, max_clauses=2)
    total = len(instances)
    passed = 0
    for inst in instances:
        NaeThreeSat.validate(inst)
        src_ans = solve_nae3sat(inst)
        red = reduce_instance(inst)
        ThreeColoring.validate(red)
        tgt_ans = solve_three_coloring(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Reduction failed on instance:")
            print(json.dumps(inst, indent=2))
            print("Source answer:", src_ans)
            print("Reduced graph:", json.dumps(red, indent=2))
            print("Target answer:", tgt_ans)
            sys.exit(1)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
