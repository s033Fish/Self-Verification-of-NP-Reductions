"""Test the SAT→Clique reduction.

The script implements tiny brute‑force solvers for the SAT and Clique
problems, generates a collection of random SAT instances (including edge
cases), reduces each instance using ``reduce`` and checks that the answers
match.  It writes a ``verdict.json`` file with the fields required by the
task description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations
from typing import List, Dict

from reduce import reduce as reduction
from problems import Sat, Clique


def sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in ``Sat``.  This implementation
    is exponential but works for the tiny instances used in the tests.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: any empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # Edge case: no clauses → trivially satisfiable.
    if not clauses:
        return True

    # Iterate over all assignments (0/1 for each variable 1..m).
    for bits in product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def clique_bruteforce(instance: Dict) -> bool:
    """Return True iff the graph contains a clique of size at least k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge‑case handling matching the specification.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Build adjacency set for O(1) edge queries.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Check all subsets of size >= k (but we can stop at k because larger
    # subsets contain a k‑clique if they are themselves a clique).
    for size in range(k, n + 1):
        for subset in combinations(range(n), size):
            # Verify every pair is adjacent.
            good = True
            for i, j in combinations(subset, 2):
                if j not in adj[i]:
                    good = False
                    break
            if good:
                return True
    return False


def generate_random_sat(max_vars: int, max_clauses: int, max_lits_per_clause: int) -> Dict:
    """Create a random SAT instance respecting the format.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        clause_len = random.randint(0, max_lits_per_clause)
        clause: List[int] = []
        for _ in range(clause_len):
            if m == 0:
                # No variables – we cannot create a literal; keep clause empty.
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

    # Deterministic edge‑case tests.
    edge_cases = [
        {"num_vars": 0, "clauses": []},  # no vars, no clauses → yes
        {"num_vars": 3, "clauses": []},  # no clauses → yes
        {"num_vars": 2, "clauses": [[]]},  # empty clause → no
        {"num_vars": 1, "clauses": [[1, -1]]},  # tautology clause → yes
        {"num_vars": 1, "clauses": [[1], [-1]]},  # contradictory clauses → no
    ]
    for instance in edge_cases:
        total += 1
        Sat.validate(instance)
        sat_ans = sat_bruteforce(instance)
        reduced = reduction(instance)
        Clique.validate(reduced)
        clique_ans = clique_bruteforce(reduced)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch on edge case", instance, sat_ans, clique_ans, file=sys.stderr)

    # Random tests.
    for _ in range(200):
        inst = generate_random_sat(max_vars=4, max_clauses=3, max_lits_per_clause=3)
        total += 1
        # Validation may raise; skip malformed (should not happen).
        try:
            Sat.validate(inst)
        except Exception as e:
            print("Invalid generated instance", inst, e, file=sys.stderr)
            continue
        sat_ans = sat_bruteforce(inst)
        reduced = reduction(inst)
        try:
            Clique.validate(reduced)
        except Exception as e:
            print("Reduction produced invalid instance", reduced, e, file=sys.stderr)
            continue
        clique_ans = clique_bruteforce(reduced)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch", inst, sat_ans, clique_ans, file=sys.stderr)

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)

if __name__ == "__main__":
    main()
