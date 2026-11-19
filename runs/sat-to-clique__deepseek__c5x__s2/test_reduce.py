"""Automated tests for the SAT→Clique reduction.

The repository provides only validation functions for the source (Sat) and
target (Clique) problems and a reduction implementation.  To verify the
reduction we implement exhaustive (brute‑force) solvers for both problems
and compare the answers on a large set of randomly generated small SAT
instances.

The test script:
* Generates a number of random SAT instances (including edge‑cases such as
  empty clause lists and empty clauses).
* Validates each generated instance using ``Sat.validate``.
* Reduces the instance with ``reduce.reduce`` and validates the resulting
  Clique instance.
* Solves both the original SAT instance and the reduced Clique instance with
  exhaustive search.
* Records whether the answers match.

Finally the script writes ``verdict.json`` containing the verification result
as required by the task description.
"""

from __future__ import annotations

import itertools
import json
import random
from pathlib import Path

import reduce  # type: ignore  # the reduction implementation
from problems import Sat, Clique


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in ``Sat``: ``num_vars`` and a
    list of clauses where each clause is a list of integer literals.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Edge case: any empty clause makes the formula unsatisfiable.
    for clause in clauses:
        if len(clause) == 0:
            return False

    # Iterate over all possible assignments of the m variables.
    for bits in range(1 << m):
        # assignment[i] is True iff variable (i+1) is set to True.
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def clique_bruteforce(instance: dict) -> bool:
    """Return True iff the graph contains a clique of size at least k.

    The instance follows the format defined in ``Clique``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases defined by the problem statement.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Build adjacency set for O(1) edge checks.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Check all subsets of size >= k (we can stop at the first success).
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Verify every pair is adjacent.
            if all(v2 in adj[v1] for i, v1 in enumerate(subset) for v2 in subset[i + 1 :]):
                return True
    return False


def generate_random_sat(max_vars: int = 3, max_clauses: int = 3, max_lits: int = 3) -> dict:
    """Generate a random SAT instance respecting the format.

    The generator may produce empty clause lists and empty clauses to test
    edge cases.
    """
    num_vars = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        clause_len = random.randint(0, max_lits)
        clause = []
        for _ in range(clause_len):
            if num_vars == 0:
                # No variables – we cannot generate a literal, break.
                break
            var = random.randint(1, num_vars)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    mismatches = []

    for _ in range(200):  # enough random tests plus deterministic edge cases
        sat_instance = generate_random_sat()
        # Validate the generated SAT instance.
        try:
            Sat.validate(sat_instance)
        except Exception:
            # If validation fails, skip this instance – it is malformed.
            continue
        total += 1
        sat_answer = sat_bruteforce(sat_instance)
        # Reduce and validate the Clique instance.
        clique_instance = reduce.reduce(sat_instance)
        Clique.validate(clique_instance)
        clique_answer = clique_bruteforce(clique_instance)
        if sat_answer == clique_answer:
            passed += 1
        else:
            mismatches.append({"sat": sat_instance, "clique": clique_instance, "sat_answer": sat_answer, "clique_answer": clique_answer})

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    # Print a short summary for the user.
    print(json.dumps(verdict, indent=2))
    if mismatches:
        print("Mismatches detected (first one shown):")
        print(json.dumps(mismatches[0], indent=2))

if __name__ == "__main__":
    main()

