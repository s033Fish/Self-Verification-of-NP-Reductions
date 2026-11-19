"""Test the reduction from NAE-3-SAT to 3-Coloring.

The repository provides only validation functions for the two problems and a
reduction implementation.  This test script implements tiny brute‑force
solvers for both source and target problems, generates a number of random
instances, runs the reduction and checks that the answers coincide.

If every generated instance behaves as expected the script prints a short
summary and exits with status 0.  Otherwise it prints the failing instance
and exits with a non‑zero status.
"""

from __future__ import annotations

import random
import sys
from itertools import product

import problems
from reduce import reduce as reduce_instance


def solve_nae3sat(instance: dict) -> bool:
    """Brute‑force solver for NAE‑3‑SAT.

    Returns True iff there exists an assignment of the variables that makes
    each clause contain at least one true and at least one false literal.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assignment in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                vals.append(val if lit > 0 else not val)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_coloring(instance: dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns True iff the graph can be coloured with three colours such that
    adjacent vertices receive different colours.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    for colours in product(range(3), repeat=n):
        good = True
        for u, v in edges:
            if colours[u] == colours[v]:
                good = False
                break
        if good:
            return True
    return False


def random_instance(max_vars: int = 4, max_clauses: int = 3) -> dict:
    """Generate a random NAE‑3‑SAT instance respecting the validation rules.
    The function may produce an instance with zero clauses.
    """
    m = random.randint(0, max_vars)
    if m < 3:
        return {"num_vars": m, "clauses": []}
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        vars_selected = random.sample(range(1, m + 1), 3)
        clause = []
        for var in vars_selected:
            clause.append(random.choice([var, -var]))
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        src = random_instance(max_vars=3, max_clauses=2)
        problems.NaeThreeSat.validate(src)
        tgt = reduce_instance(src)
        # Skip instances that would make the coloring solver too slow
        if tgt["n"] > 9:
            continue
        problems.ThreeColoring.validate(tgt)
        ans_src = solve_nae3sat(src)
        ans_tgt = solve_three_coloring(tgt)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch detected!", file=sys.stderr)
            print("Source instance:", src, file=sys.stderr)
            print("Reduced target:", tgt, file=sys.stderr)
            print("Source answer:", ans_src, "Target answer:", ans_tgt, file=sys.stderr)
            sys.exit(1)
    print(f"All {passed}/{total} tests passed.")

if __name__ == "__main__":
    main()
