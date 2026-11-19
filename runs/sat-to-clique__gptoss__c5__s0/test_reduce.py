"""Automated tests for the SAT-to-Clique reduction.

The repository provides only validation functions for the two problems.
This test module implements brute‑force solvers for SAT and Clique based on
the formal definitions in ``problems.py`` and then checks that the reduction
implemented in ``reduce.py`` preserves the answer on a wide range of small
random instances.

The script is executed directly by the evaluation harness.  It prints a JSON
object compatible with the required ``verdict.json`` format.
"""

from __future__ import annotations

import json
import random
import itertools
import sys
from typing import List, Dict, Any

from problems import Sat, Clique
from reduce import reduce as reduce_instance


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in ``Sat``: ``num_vars`` and a
    list of clauses where each clause is a list of integer literals.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: a formula with no clauses is trivially satisfiable.
    if not clauses:
        return True

    # Enumerate all possible assignments as bit masks.
    for mask in range(1 << m):
        # assignment[var] = True/False for var indexed from 1.
        assignment = [(mask >> (var - 1)) & 1 == 1 for var in range(1, m + 1)]
        ok = True
        for clause in clauses:
            # Empty clause is never satisfied.
            if not clause:
                ok = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var - 1]
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


def clique_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph contains a clique of size at least k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from definition.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Build adjacency set for O(1) edge checks.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    # Check all subsets of size k (larger subsets would also contain a k‑clique).
    for subset in itertools.combinations(range(n), k):
        ok = True
        for i, j in itertools.combinations(subset, 2):
            if not adj[i][j]:
                ok = False
                break
        if ok:
            return True
    return False


def random_sat_instance(max_vars: int, max_clauses: int, max_lits_per_clause: int) -> Dict[str, Any]:
    """Generate a random SAT instance respecting the validation rules.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # Randomly decide clause length (including possibility of empty clause).
        length = random.randint(0, max_lits_per_clause)
        clause = []
        for _ in range(length):
            if m == 0:
                # No variables available – skip adding literals.
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0

    # Exhaustively test all tiny instances (vars up to 3, clauses up to 3, lits up to 2).
    for m in range(0, 4):
        for num_clauses in range(0, 4):
            # Generate all possible clause lists (including duplicates) by
            # iterating over product of possible literals.
            # To keep the enumeration finite, we limit literals per clause to 0..2.
            literals = []
            for var in range(1, m + 1):
                literals.extend([var, -var])
            # Build clause options: empty, single literal, double literals.
            clause_options: List[List[int]] = [[]]
            for lit in literals:
                clause_options.append([lit])
            for lit1 in literals:
                for lit2 in literals:
                    clause_options.append([lit1, lit2])
            for clauses in itertools.product(clause_options, repeat=num_clauses):
                instance = {"num_vars": m, "clauses": list(clauses)}
                try:
                    Sat.validate(instance)
                except Exception:
                    continue
                tests_run += 1
                sat_ans = sat_bruteforce(instance)
                reduced = reduce_instance(instance)
                Clique.validate(reduced)
                clique_ans = clique_bruteforce(reduced)
                if sat_ans == clique_ans:
                    tests_passed += 1
                else:
                    print("Mismatch!", file=sys.stderr)
                    print("SAT instance:", instance, file=sys.stderr)
                    print("Reduced:", reduced, file=sys.stderr)
                    print("SAT answer:", sat_ans, "Clique answer:", clique_ans, file=sys.stderr)

    # Additionally run a number of random larger instances.
    for _ in range(200):
        inst = random_sat_instance(max_vars=5, max_clauses=5, max_lits_per_clause=3)
        try:
            Sat.validate(inst)
        except Exception:
            continue
        tests_run += 1
        sat_ans = sat_bruteforce(inst)
        reduced = reduce_instance(inst)
        Clique.validate(reduced)
        clique_ans = clique_bruteforce(reduced)
        if sat_ans == clique_ans:
            tests_passed += 1
        else:
            print("Random mismatch!", file=sys.stderr)
            print(inst, file=sys.stderr)
            print(reduced, file=sys.stderr)
            print(sat_ans, clique_ans, file=sys.stderr)

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
