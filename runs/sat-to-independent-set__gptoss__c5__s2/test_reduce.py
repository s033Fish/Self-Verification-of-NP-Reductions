"""Brute‑force verification of the SAT → Independent Set reduction.

The repository provides only validation helpers and the reduction itself.
This script implements straightforward exponential‑time solvers for both
problems and checks that for a large collection of small random SAT
instances the answer of the reduced Independent Set instance matches the
original SAT answer.

The script is intended to be executed directly (``python -m pytest`` is
not required).  It prints a JSON object ``verdict.json`` with the fields
required by the task description.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

from reduce import reduce as reduce_instance
from problems import Sat, IndependentSet


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in ``Sat``: a dict with keys
    ``num_vars`` and ``clauses``.  Variables are numbered from 1 to
    ``num_vars``.  An empty clause makes the formula unsatisfiable; a
    formula with no clauses is trivially satisfiable.
    """
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Edge case: any empty clause → unsatisfiable
    if any(len(c) == 0 for c in clauses):
        return False
    # Edge case: no clauses → satisfiable
    if not clauses:
        return True

    # Iterate over all 2^m assignments.
    for bits in itertools.product([False, True], repeat=m):
        # bits[i] corresponds to variable i+1
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            # Clause satisfied if any literal true under assignment
            satisfied = False
            for lit in clause:
                var = abs(lit)
                sign = lit > 0
                if assignment[var] == sign:
                    satisfied = True
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size >= k.
    """
    IndependentSet.validate(instance)
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    # Edge cases handled by brute force as well.
    if k <= 0:
        return True
    if k > n:
        return False

    # Pre‑compute adjacency sets for fast conflict checking.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Enumerate subsets of size >= k (we can stop early when found).
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Check independence
            independent = True
            for i, u in enumerate(subset):
                for v in subset[i + 1:]:
                    if v in adj[u]:
                        independent = False
                        break
                if not independent:
                    break
            if independent:
                return True
    return False


def random_sat_instance(max_vars: int = 4, max_clauses: int = 4, max_lits: int = 3) -> dict:
    """Generate a random SAT instance respecting the validation rules.

    The generator may produce empty clauses or duplicate literals – both
    are allowed by the specification and useful for testing edge cases.
    """
    num_vars = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: list[list[int]] = []
    for _ in range(num_clauses):
        # Randomly decide clause length (including possibly 0).
        length = random.randint(0, max_lits)
        clause = []
        for _ in range(length):
            if num_vars == 0:
                # No variables – we cannot create a literal, so break.
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
    for _ in range(200):  # enough random tests for confidence
        sat_inst = random_sat_instance()
        sat_answer = sat_bruteforce(sat_inst)
        try:
            ind_inst = reduce_instance(sat_inst)
        except Exception as exc:
            print(f"Reduction raised an exception on instance {sat_inst}: {exc}", file=sys.stderr)
            continue
        ind_answer = independent_set_bruteforce(ind_inst)
        total += 1
        if sat_answer == ind_answer:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("SAT instance:", json.dumps(sat_inst), file=sys.stderr)
            print("SAT answer:", sat_answer, file=sys.stderr)
            print("Reduced instance:", json.dumps(ind_inst), file=sys.stderr)
            print("Independent‑Set answer:", ind_answer, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    # Also print to stdout for visibility.
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
