"""Test suite for the reduction from ThreeSat to IndependentSet.

The repository provides only validation functions for the two problems and
the reduction implementation.  To verify that the reduction is correct we
implement simple exhaustive solvers for both problems and compare the
answers on a collection of randomly generated small instances.

The script writes a ``verdict.json`` file with the fields required by the task description:

    {
        "verified": <bool>,
        "tests_run": <int>,
        "tests_passed": <int>
    }

If every generated test case satisfies that the answer to the original
ThreeSat instance equals the answer to the reduced IndependentSet instance,
``verified`` is true.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations
from typing import List, Dict, Any

import problems  # The module containing the problem definitions
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    """Exhaustive solver for 3‑SAT.

    Returns True iff there exists an assignment to the variables that makes
    every clause contain at least one true literal.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate all 2^m assignments (0 = false, 1 = true)
    for bits in product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            # Clause satisfied if any literal evaluates to True
            if not any((assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)]) for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance: Dict[str, Any]) -> bool:
    """Exhaustive solver for Independent Set.

    Returns True iff the graph contains an independent set of size at least
    ``k``.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    # Quick edge‑case handling
    if k <= 0:
        return True
    if k > n:
        return False

    # Check all subsets of size >= k (but we can stop as soon as we find one)
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in combinations(vertices, size):
            # Verify independence
            independent = True
            for u, v in combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    independent = False
                    break
            if independent:
                return True
    return False


def generate_random_three_sat(max_vars: int, max_clauses: int) -> Dict[str, Any]:
    """Generate a random valid 3‑SAT instance.

    The generator respects the constraints documented in ``ThreeSat.validate``:
    each clause contains exactly three literals on three distinct variables
    and never contains both a variable and its negation.
    """
    m = random.randint(0, max_vars)
    # If we have clauses, we need at least 3 variables per the problem statement.
    if m < 3:
        # Allow zero clauses regardless of m; otherwise ensure m>=3.
        num_clauses = 0
    else:
        num_clauses = random.randint(0, max_clauses)

    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # Choose three distinct variables
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clause = []
        for var in vars_in_clause:
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # Deterministic for reproducibility
    total = 0
    passed = 0
    # We'll generate a reasonable number of tests covering small sizes.
    for _ in range(200):
        instance = generate_random_three_sat(max_vars=5, max_clauses=5)
        # Validate the generated instance using the provided validator.
        try:
            problems.ThreeSat.validate(instance)
        except Exception as e:
            print("Generated invalid instance:", instance, file=sys.stderr)
            raise
        three_sat_answer = solve_three_sat(instance)
        reduced = reduce_instance(instance)
        # Validate the reduced instance as an IndependentSet instance.
        problems.IndependentSet.validate(reduced)
        indep_answer = solve_independent_set(reduced)
        total += 1
        if three_sat_answer == indep_answer:
            passed += 1
        else:
            # Print details for debugging.
            print("Mismatch!", file=sys.stderr)
            print("ThreeSat instance:", json.dumps(instance), file=sys.stderr)
            print("Reduced instance:", json.dumps(reduced), file=sys.stderr)
            print("ThreeSat answer:", three_sat_answer, file=sys.stderr)
            print("IndependentSet answer:", indep_answer, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)

if __name__ == "__main__":
    main()

