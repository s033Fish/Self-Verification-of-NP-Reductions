"""Automated tests for the NAE-3-SAT to 3-Coloring reduction.

The repository provides a ``reduce`` function that maps a NAE‑3‑SAT instance
to a tiny graph (K3 or K4).  To verify the reduction we implement brute‑force
solvers for both source and target problems and compare answers on a large
set of randomly generated instances.

The test script is deliberately self‑contained – it does not rely on any
external libraries beyond the Python standard library and the local modules
``problems`` and ``reduce``.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import Dict, List, Any

# Import the modules under test.
from problems import NaeThreeSat, ThreeColoring
from reduce import reduce as reduce_instance


def naesat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the NAE‑3‑SAT instance is satisfiable.

    This implementation mirrors the helper in ``reduce.py`` but is kept
    separate to avoid any accidental dependence on that code.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                vals.append(val if lit > 0 else not val)
            # NAE condition: not all equal
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def three_coloring_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph is 3‑colorable.

    Tries every assignment of colours {0,1,2} to the vertices.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    for coloring in product(range(3), repeat=n):
        good = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                good = False
                break
        if good:
            return True
    return False


def random_instance(num_vars: int, num_clauses: int) -> Dict[str, Any]:
    """Generate a random NAE‑3‑SAT instance respecting the validation rules.

    Each clause consists of three distinct variables with random signs.
    """
    clauses = []
    for _ in range(num_clauses):
        vars_ = random.sample(range(1, num_vars + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    # Test a variety of small sizes, including edge cases.
    for num_vars in range(0, 5):
        max_clauses = 4
        for num_clauses in range(0, max_clauses + 1):
            for _ in range(20):
                # Ensure we have enough variables for clauses; if not, skip.
                if num_vars < 3 and num_clauses > 0:
                    continue
                instance = random_instance(num_vars, num_clauses)
                try:
                    NaeThreeSat.validate(instance)
                except Exception:
                    continue
                total += 1
                src_ans = naesat_bruteforce(instance)
                try:
                    target = reduce_instance(instance)
                except Exception as e:
                    print(f"Reduction raised an exception: {e}", file=sys.stderr)
                    continue
                try:
                    ThreeColoring.validate(target)
                except Exception as e:
                    print(f"Target validation failed: {e}", file=sys.stderr)
                    continue
                tgt_ans = three_coloring_bruteforce(target)
                if src_ans == tgt_ans:
                    passed += 1
                else:
                    print("Mismatch!", file=sys.stderr)
                    print("Source instance:", json.dumps(instance), file=sys.stderr)
                    print("Source answer:", src_ans, file=sys.stderr)
                    print("Reduced target:", json.dumps(target), file=sys.stderr)
                    print("Target answer:", tgt_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

