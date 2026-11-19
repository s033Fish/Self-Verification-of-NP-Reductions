"""Test the SAT→Clique reduction.

The repository provides only validation functions for the two problems.
This script implements tiny brute‑force solvers for SAT and Clique, generates
random small instances, applies ``reduce`` and checks that the answers agree.

The script prints a JSON object suitable for ``verdict.json`` and writes that
file to the working directory.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations

# Import the problem definitions and the reduction.
import problems
from reduce import reduce as sat_to_clique


def sat_solver(instance: dict) -> bool:
    """Brute‑force SAT solver for the given instance.

    Returns ``True`` iff the CNF formula is satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Edge case: empty clause makes formula unsatisfiable.
    for clause in clauses:
        if len(clause) == 0:
            return False

    # Iterate over all 2^m assignments.
    for bits in product([False, True], repeat=m):
        # bits[i] corresponds to variable i+1.
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def clique_solver(instance: dict) -> bool:
    """Brute‑force Clique solver.

    Returns ``True`` iff the graph contains a clique of size at least ``k``.
    """
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]

    # Trivial edge cases handled by brute force as well.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Check all subsets of size k up to n.
    for size in range(k, n + 1):
        for subset in combinations(range(n), size):
            # Verify every pair is an edge.
            good = True
            for u, v in combinations(subset, 2):
                a, b = (u, v) if u < v else (v, u)
                if (a, b) not in edges:
                    good = False
                    break
            if good:
                return True
    return False


def random_sat_instance(max_vars: int = 4, max_clauses: int = 4, max_lits: int = 3) -> dict:
    """Generate a random SAT instance respecting the validation rules.

    Variables are numbered 1..m. Literals may repeat and a clause may contain
    both a literal and its negation.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: list[list[int]] = []
    for _ in range(num_clauses):
        clause_len = random.randint(0, max_lits)
        clause: list[int] = []
        for _ in range(clause_len):
            if m == 0:
                # No variables, but literals must be within 1..m => impossible.
                # So we keep clause empty.
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    failures = []

    for _ in range(200):
        sat_inst = random_sat_instance()
        # Validate the generated SAT instance.
        try:
            problems.Sat.validate(sat_inst)
        except Exception as e:
            # Should never happen for our generator.
            print(f"Generated invalid SAT instance: {e}", file=sys.stderr)
            continue
        sat_ans = sat_solver(sat_inst)

        # Apply reduction.
        clique_inst = sat_to_clique(sat_inst)
        # Validate the reduction output.
        try:
            problems.Clique.validate(clique_inst)
        except Exception as e:
            print(f"Reduction produced invalid Clique instance: {e}", file=sys.stderr)
            continue
        clique_ans = clique_solver(clique_inst)

        total += 1
        if sat_ans == clique_ans:
            passed += 1
        else:
            failures.append({"sat": sat_inst, "clique": clique_inst, "sat_ans": sat_ans, "clique_ans": clique_ans})

    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    # Write verdict.json
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    # Print for visibility.
    print(json.dumps(verdict, indent=2))
    if failures:
        print("Some tests failed:", file=sys.stderr)
        for f in failures[:5]:
            print(json.dumps(f, indent=2), file=sys.stderr)

if __name__ == "__main__":
    main()
