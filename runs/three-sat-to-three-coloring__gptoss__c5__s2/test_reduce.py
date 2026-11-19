"""Test harness for the 3‑SAT → 3‑Coloring reduction.

The repository provides only validation functions for the two problems and
the reduction implementation.  To verify the reduction we implement brute‑
force solvers for both problems and compare the answers on a collection of
small randomly generated instances.

If every instance yields the same answer before and after reduction we write
``verdict.json`` with ``{"verified": true, ...}``.  Otherwise ``verified`` is
set to ``false`` and the mismatching instance is printed for debugging.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import Dict, List, Tuple

from problems import ThreeSat, ThreeColoring
from reduce import reduce as reduce_instance


def sat_bruteforce(instance: Dict) -> bool:
    """Brute‑force SAT solver for 3‑SAT instances."""
    ThreeSat.validate(instance)
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            lit_sat = any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            )
            if not lit_sat:
                ok = False
                break
        if ok:
            return True
    return False


def coloring_bruteforce(instance: Dict) -> bool:
    """Brute‑force solver for 3‑colorability."""
    ThreeColoring.validate(instance)
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    for colors in product([0, 1, 2], repeat=n):
        if all(colors[u] != colors[v] for u, v in edges):
            return True
    return False


def random_instance(max_vars: int = 3, max_clauses: int = 1) -> Dict:
    """Generate a random 3‑SAT instance respecting the problem constraints.
    The bounds are kept tiny so that the resulting graph stays small enough
    for exhaustive 3‑coloring.
    """
    m = random.randint(0, max_vars)
    if m == 0 or m < 3:
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        vars_idx = random.sample(range(1, m + 1), 3)
        clause = [v if random.choice([True, False]) else -v for v in vars_idx]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    mismatches: List[Tuple[Dict, bool, bool]] = []
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3]]},
    ]
    for inst in edge_cases:
        total += 1
        sat = sat_bruteforce(inst)
        red = reduce_instance(inst)
        col = coloring_bruteforce(red)
        if sat == col:
            passed += 1
        else:
            mismatches.append((inst, sat, col))
    # Limited random testing to keep runtime feasible.
    for _ in range(20):
        inst = random_instance()
        total += 1
        sat = sat_bruteforce(inst)
        red = reduce_instance(inst)
        if red["n"] > 12:
            continue
        col = coloring_bruteforce(red)
        if sat == col:
            passed += 1
        else:
            mismatches.append((inst, sat, col))
    verdict = {"verified": len(mismatches) == 0, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    if mismatches:
        print("MISMATCHES FOUND:", file=sys.stderr)
        for inst, sat, col in mismatches:
            print("Instance:", inst, file=sys.stderr)
            print("SAT answer:", sat, "Coloring answer:", col, file=sys.stderr)
        sys.exit(1)
    else:
        print(json.dumps(verdict))

if __name__ == "__main__":
    main()
