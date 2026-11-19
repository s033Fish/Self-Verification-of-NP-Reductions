"""Test suite for the NAE-3-SAT to 3-Coloring reduction.

The purpose of this file is to independently verify that ``reduce.py``
correctly maps any NAE-3-SAT instance to a 3‑Coloring instance such that the
answers (YES/NO) coincide.

We provide brute‑force solvers for both problems based directly on the
definitions in ``problems.py`` and then generate a number of random small
instances. For each instance we compare the solver's answer on the original
problem with the answer on the reduced graph.

The script records how many tests were executed and how many passed and
produces ``verdict.json`` in the required format.
"""

from __future__ import annotations

import json
import random
import sys
from typing import List, Dict, Any

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce as reduce_instance


def solve_nae_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for NAE‑3‑SAT.

    Returns ``True`` iff there exists an assignment to the variables that
    satisfies the not‑all‑equal condition for every clause.
    """
    num_vars = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for mask in range(1 << num_vars):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit)
                val = bool(mask & (1 << (var - 1)))
                lit_true = (lit > 0 and val) or (lit < 0 and not val)
                vals.append(lit_true)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_coloring(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns ``True`` iff the graph can be coloured with three colours such
    that adjacent vertices receive different colours.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    for mask in range(3 ** n):
        colours = []
        tmp = mask
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


def random_instance(max_vars: int = 3, max_clauses: int = 2) -> Dict[str, Any]:
    """Generate a random valid NAE‑3‑SAT instance.

    The generator respects the validation rules from ``problems.py``.
    """
    num_vars = random.randint(0, max_vars)
    # Ensure at least 3 variables when we may create a clause.
    if num_vars < 3:
        num_vars = 3
    clauses: List[List[int]] = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        vars_in_clause = random.sample(range(1, num_vars + 1), 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    edge_cases: List[Dict[str, Any]] = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3]]},
    ]
    for inst in edge_cases:
        total += 1
        try:
            NaeThreeSat.validate(inst)
        except Exception as e:
            print(f"Edge case validation failed: {inst} -> {e}", file=sys.stderr)
            continue
        ans_src = solve_nae_three_sat(inst)
        red = reduce_instance(inst)
        ThreeColoring.validate(red)
        ans_tgt = solve_three_coloring(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch on edge case", inst, ans_src, ans_tgt, file=sys.stderr)

    for _ in range(200):
        inst = random_instance()
        est_n = 3 + 2 * inst["num_vars"] + 3 * len(inst["clauses"])
        if est_n > 12:
            continue
        total += 1
        try:
            NaeThreeSat.validate(inst)
        except Exception:
            continue
        ans_src = solve_nae_three_sat(inst)
        red = reduce_instance(inst)
        ThreeColoring.validate(red)
        ans_tgt = solve_three_coloring(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch on random instance", inst, ans_src, ans_tgt, file=sys.stderr)

    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
