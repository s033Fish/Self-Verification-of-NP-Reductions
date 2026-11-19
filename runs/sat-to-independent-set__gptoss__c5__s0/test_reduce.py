"""Automated tests for the SAT → Independent Set reduction.

The repository provides only validation functions for the two problems.
This test suite implements tiny brute‑force solvers for SAT and Independent
Set, generates a number of random SAT instances, runs the supplied ``reduce``
function and checks that the answer to the produced Independent‑Set instance
matches the answer to the original SAT instance.

If every generated test passes we write ``verdict.json`` with ``verified``
set to ``true``; otherwise ``verified`` is ``false``.  The file also contains
the total number of tests run and how many passed.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations
from typing import List, Dict

from problems import Sat, IndependentSet
from reduce import reduce as reduce_instance


def sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in ``Sat``: ``num_vars`` variables
    numbered 1..m and a list of clauses, each clause a list of integer literals.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Edge case: empty clause makes it unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # No clauses → trivially satisfiable.
    if not clauses:
        return True

    for assignment in product([False, True], repeat=m):
        # assignment[i] corresponds to variable i+1
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
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


def independent_set_bruteforce(instance: Dict) -> bool:
    """Return True iff the graph has an independent set of size at least k.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False

    # Pre‑compute adjacency set for fast checks.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Enumerate subsets of vertices; stop early when we find a large enough set.
    for r in range(k, n + 1):
        for combo in combinations(range(n), r):
            independent = True
            for i in range(len(combo)):
                for j in range(i + 1, len(combo)):
                    if combo[j] in adj[combo[i]]:
                        independent = False
                        break
                if not independent:
                    break
            if independent:
                return True
    return False


def generate_random_sat(max_vars: int = 4, max_clauses: int = 4, max_lit_per: int = 3) -> Dict:
    """Create a random SAT instance respecting the validation rules.
    Variables are numbered 1..m. Literals are non‑zero and within the range.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # Randomly decide clause length (including possibility of empty clause)
        length = random.randint(0, max_lit_per)
        clause = []
        for _ in range(length):
            if m == 0:
                # No variables, but we can still add a literal 0? Validation forbids 0.
                # So we keep clause empty in this case.
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 200
    passed = 0
    for _ in range(total):
        sat_instance = generate_random_sat()
        # Validate the generated instance (should pass).
        Sat.validate(sat_instance)
        sat_ans = sat_bruteforce(sat_instance)
        # Reduce and validate target.
        target_instance = reduce_instance(sat_instance)
        IndependentSet.validate(target_instance)
        target_ans = independent_set_bruteforce(target_instance)
        if sat_ans == target_ans:
            passed += 1
        else:
            # Print the failing case for debugging.
            print("Mismatch!", file=sys.stderr)
            print("SAT instance:", sat_instance, file=sys.stderr)
            print("SAT answer:", sat_ans, file=sys.stderr)
            print("Reduced instance:", target_instance, file=sys.stderr)
            print("IS answer:", target_ans, file=sys.stderr)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    # Also print the verdict for visibility.
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

