"""Test suite for the reduction from ThreeSat to Clique.

The repository provides only validation helpers and the reduction implementation.
To verify the reduction we implement straightforward brute‑force solvers for both
source (ThreeSat) and target (Clique) problems, generate a variety of small
instances, run the reduction and compare the answers.

If every generated instance yields matching answers we consider the reduction
verified and write a ``verdict.json`` file with the results.
"""

from __future__ import annotations

import json
import random
import itertools
from typing import List, Dict, Tuple

from problems import SOURCE, TARGET
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict) -> bool:
    """Brute‑force SAT solver for the ThreeSat instance.

    Returns True iff there exists an assignment to the variables that satisfies
    every clause.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate all possible assignments as bit‑vectors of length m.
    for bits in range(1 << m):
        # assignment[v] = True/False for variable v (1‑based)
        assignment = [(bits >> (v - 1)) & 1 == 1 for v in range(1, m + 1)]
        ok = True
        for clause in clauses:
            # clause is satisfied if any literal evaluates to True.
            lit_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0:
                    lit_sat = lit_sat or val
                else:
                    lit_sat = lit_sat or (not val)
                if lit_sat:
                    break
            if not lit_sat:
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance: Dict) -> bool:
    """Brute‑force check whether the graph has a clique of size at least k.
    """
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Check all subsets of size k (larger subsets would also contain a k‑subset)
    vertices = list(range(n))
    for combo in itertools.combinations(vertices, k):
        # verify every pair is an edge
        all_edges = True
        for u, v in itertools.combinations(combo, 2):
            a, b = (u, v) if u < v else (v, u)
            if (a, b) not in edges:
                all_edges = False
                break
        if all_edges:
            return True
    return False


def random_three_sat_instance(max_vars: int, max_clauses: int) -> Dict:
    """Generate a random valid ThreeSat instance.

    The generator respects the constraints: each clause has exactly three
    literals on distinct variables and does not contain a variable together
    with its negation.
    """
    m = random.randint(0, max_vars)
    # Ensure at least 3 variables when we generate clauses (otherwise no clause can be formed)
    if m < 3:
        m = 0
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        if m == 0:
            # No variables, but we still need a clause – impossible, so break
            break
        # pick three distinct variables
        vars_selected = random.sample(range(1, m + 1), 3)
        clause = []
        for var in vars_selected:
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_trials: int = 200) -> Tuple[int, int]:
    passed = 0
    total = 0
    for _ in range(num_trials):
        instance = random_three_sat_instance(max_vars=4, max_clauses=4)
        # Validate using the provided validator (will raise if malformed)
        SOURCE.validate(instance)  # type: ignore[attr-defined]
        # Compute answers
        ans_sat = solve_three_sat(instance)
        reduced = reduce_instance(instance)
        # Validate reduced instance as well
        TARGET.validate(reduced)  # type: ignore[attr-defined]
        ans_clique = solve_clique(reduced)
        total += 1
        if ans_sat == ans_clique:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, ans_sat, ans_clique)
    return total, passed


if __name__ == "__main__":
    total, passed = run_tests(500)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
