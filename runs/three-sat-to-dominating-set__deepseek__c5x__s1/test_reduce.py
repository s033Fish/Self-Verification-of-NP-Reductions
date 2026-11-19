"""Test the reduction from ThreeSat to DominatingSet.

The repository provides only the problem definitions and a claimed reduction.
This script implements tiny brute‑force solvers for both problems and checks
that for a wide range of small random instances the answer of the reduced
DominatingSet instance matches the answer of the original ThreeSat instance.

If every test passes we consider the reduction verified and write a verdict
file as required by the task description.
"""

from __future__ import annotations

import json
import random
import itertools
import sys
from pathlib import Path

# Import the problem definitions and the reduction implementation.
import problems  # type: ignore
import reduce  # type: ignore


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force SAT solver for the 3‑SAT instance format.

    Returns True iff there exists an assignment of the variables that satisfies
    every clause.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Iterate over all 2^m assignments.
    for bits in range(1 << m):
        # assignment[i] is True iff variable (i+1) is True.
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            # clause is a list of three literals.
            lit_true = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0:
                    lit_true = lit_true or val
                else:
                    lit_true = lit_true or (not val)
            if not lit_true:
                ok = False
                break
        if ok:
            return True
    return False


def solve_dominating_set(instance: dict) -> bool:
    """Brute‑force solver for Dominating Set.

    Returns True iff there exists a dominating set of size at most k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    # Build adjacency list (including self for convenience).
    adj = [set([v]) for v in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # If k < 0, answer is always False (handled by brute force as well).
    if k < 0:
        return False
    # Enumerate subsets up to size k.
    vertices = list(range(n))
    for r in range(0, min(k, n) + 1):
        for combo in itertools.combinations(vertices, r):
            dominated = set()
            for v in combo:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def random_three_sat_instance(max_vars: int, max_clauses: int) -> dict:
    """Generate a random well‑formed 3‑SAT instance.

    The generator respects the constraints of the problem definition:
    * each clause has exactly three literals on distinct variables.
    * no clause contains both a variable and its negation.
    """
    m = random.randint(0, max_vars)
    # Ensure that if there are clauses we have at least 3 variables.
    if m > 0 and m < 3:
        m = 3
    t = random.randint(0, max_clauses)
    clauses = []
    for _ in range(t):
        # Choose three distinct variables.
        vars_ = random.sample(range(1, m + 1), 3) if m >= 3 else []
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        if clause:
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):  # number of random tests
        inst = random_three_sat_instance(max_vars=4, max_clauses=3)
        # Validate the source instance using the provided validator.
        try:
            problems.ThreeSat.validate(inst)
        except Exception:
            # Skip malformed instances (should be rare).
            continue
        three_sat_answer = solve_three_sat(inst)
        # Reduce and validate target.
        reduced = reduce.reduce(inst)
        problems.DominatingSet.validate(reduced)
        dominating_answer = solve_dominating_set(reduced)
        total += 1
        if three_sat_answer == dominating_answer:
            passed += 1
        else:
            print("Mismatch!", json.dumps({"source": inst, "reduced": reduced}), file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

