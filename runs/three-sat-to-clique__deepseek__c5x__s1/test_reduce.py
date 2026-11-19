"""Test the correctness of the reduction from 3‑SAT to Clique.

The test suite enumerates a large number of small, valid 3‑SAT instances,
applies the provided ``reduce`` function, and then checks that the answers
to the original and reduced instances agree.  Brute‑force solvers for both
problems are implemented directly in this file – the repository does not
provide any.

The script is intended to be run directly.  It writes a ``verdict.json``
file containing the verification result, the number of tests that were run
and how many passed.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

import problems  # The module that defines ``ThreeSat`` and ``Clique``
import reduce  # The reduction to be verified


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    Returns ``True`` iff there exists an assignment to the variables that
    satisfies all clauses.
    """
    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate all 2^m possible assignments (True/False represented by 1/0).
    for bits in range(1 << m):
        # assignment[v] is True if variable v+1 is set to True.
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            # Clause is satisfied if any literal evaluates to True.
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


def solve_clique(instance: dict) -> bool:
    """Brute‑force solver for Clique.

    Returns ``True`` iff the graph contains a clique of size at least ``k``.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # Build adjacency set for O(1) edge checks.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Check all subsets of size >= k (we can stop at exactly k because adding
    # more vertices can only make the condition harder to satisfy).
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            # Verify every pair is adjacent.
            if all((v in adj[u]) for u, v in itertools.combinations(combo, 2)):
                return True
    return False


def generate_three_sat_instances(max_vars: int = 4, max_clauses: int = 3):
    """Yield all valid 3‑SAT instances with up to ``max_vars`` variables and
    up to ``max_clauses`` clauses.  Instances are yielded as dictionaries that
    conform to the format expected by ``ThreeSat.validate``.
    """
    for m in range(max_vars + 1):
        # All possible literals for the given number of variables.
        literals = []
        for var in range(1, m + 1):
            literals.extend([var, -var])
        # Generate all possible clauses (3 distinct variables, any sign).
        clause_set = []
        for vars_combo in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                clause = [signs[i] * vars_combo[i] for i in range(3)]
                clause_set.append(clause)
        # Include the empty clause list (no clauses) as a valid instance.
        for num_clauses in range(max_clauses + 1):
            if num_clauses == 0:
                yield {"num_vars": m, "clauses": []}
                continue
            # Produce all possible lists of ``num_clauses`` clauses (allowing
            # repetitions via product).
            for clauses in itertools.product(clause_set, repeat=num_clauses):
                yield {"num_vars": m, "clauses": [list(c) for c in clauses]}


def main() -> None:
    total = 0
    passed = 0
    for instance in generate_three_sat_instances():
        total += 1
        # Validate the original instance using the provided validator.
        try:
            problems.ThreeSat.validate(instance)
        except Exception as exc:
            print(f"Invalid generated instance: {exc}", file=sys.stderr)
            continue
        # Compute answers.
        three_sat_answer = solve_three_sat(instance)
        reduced = reduce.reduce(instance)
        # Validate the reduced instance.
        try:
            problems.Clique.validate(reduced)
        except Exception as exc:
            print(f"Reduction produced invalid instance: {exc}", file=sys.stderr)
            continue
        clique_answer = solve_clique(reduced)
        if three_sat_answer == clique_answer:
            passed += 1
        else:
            print("Mismatch detected:")
            print("3‑SAT instance:", json.dumps(instance))
            print("Reduced instance:", json.dumps(reduced))
            print("3‑SAT answer:", three_sat_answer)
            print("Clique answer:", clique_answer)
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

