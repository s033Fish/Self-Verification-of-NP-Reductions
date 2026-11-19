"""Automated tests for the reduction from ThreeSat to VertexCover.

The repository provides only validation functions.  To verify the reduction
implemented in ``reduce.py`` we need independent (brute‑force) solvers for the
source and target problems.  The tests generate a variety of small random
instances of 3‑SAT, reduce each instance, solve both the original and the
reduced instance, and assert that the answers match.

If all generated instances pass, the reduction is considered verified and the
script exits with status 0.  The number of tests run and passed are recorded in
``verdict.json``.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations
from typing import List, Dict

from problems import ThreeSat, VertexCover
from reduce import reduce as reduce_instance


def three_sat_solver(instance: Dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    Returns ``True`` iff there exists an assignment to the ``num_vars``
    variables that satisfies every clause.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate all 2^m assignments as a tuple of booleans where index i
    # corresponds to variable i+1.
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # Clause is satisfied if any literal evaluates to True.
            lit_true = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0:
                    lit_true = lit_true or val
                else:
                    lit_true = lit_true or (not val)
                if lit_true:
                    break
            if not lit_true:
                ok = False
                break
        if ok:
            return True
    return False


def vertex_cover_solver(instance: Dict) -> bool:
    """Brute‑force solver for Vertex Cover.

    Returns ``True`` iff there exists a vertex cover of size at most ``k``.
    """
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    # Enumerate subsets of vertices up to size k.
    for size in range(0, min(k, n) + 1):
        for subset in combinations(range(n), size):
            s = set(subset)
            covered = True
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False


def generate_random_three_sat(max_vars: int = 4, max_clauses: int = 5) -> Dict:
    """Create a random 3‑SAT instance respecting the problem constraints.

    * ``max_vars`` – maximum number of variables (inclusive).
    * ``max_clauses`` – maximum number of clauses (inclusive).
    """
    m = random.randint(0, max_vars)
    # If there are clauses we need at least 3 variables according to the spec.
    if m < 3:
        # Allow zero‑clause formulas even with fewer variables.
        c = random.choice([0, random.randint(0, max_clauses)])
        if c > 0:
            # ensure at least 3 variables for non‑empty clause set
            m = 3
    else:
        c = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(c):
        # Choose three distinct variables.
        vars_selected = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_selected:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    tests_run = 0
    tests_passed = 0
    # Generate a mixture of deterministic edge‑case instances and random ones.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3], [1, -2, -3]]},
    ]
    for instance in edge_cases:
        tests_run += 1
        try:
            ThreeSat.validate(instance)
        except Exception as e:
            print("Validation failed on edge case", instance, e)
            continue
        sat = three_sat_solver(instance)
        reduced = reduce_instance(instance)
        vc = vertex_cover_solver(reduced)
        if sat == vc:
            tests_passed += 1
        else:
            print("Mismatch on edge case", instance, sat, vc)

    # Random tests
    for _ in range(200):
        instance = generate_random_three_sat()
        try:
            ThreeSat.validate(instance)
        except Exception:
            continue
        tests_run += 1
        sat = three_sat_solver(instance)
        reduced = reduce_instance(instance)
        vc = vertex_cover_solver(reduced)
        if sat == vc:
            tests_passed += 1
        else:
            print("Mismatch on random instance", instance, sat, vc)
            break

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
    sys.exit(0 if verdict["verified"] else 1)

if __name__ == "__main__":
    main()
