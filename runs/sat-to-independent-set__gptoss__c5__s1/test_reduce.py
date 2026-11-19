"""Test suite for the SAT → Independent Set reduction.

The repository provides only the problem definitions and the reduction
function.  To verify the correctness of ``reduce.py`` we implement
straight‑forward brute‑force solvers for both source and target problems
and compare their answers on a collection of small randomly generated
SAT instances.

The tests count how many instances were examined and how many passed.
The results are written to ``verdict.json`` as required by the task
description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations
from typing import List, Dict, Any

from problems import Sat, IndependentSet
from reduce import reduce as reduce_instance


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in ``Sat``.  We iterate over
    all possible assignments of the ``num_vars`` variables (which is fine
    for the tiny instances used in the test suite).
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Edge case: an empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # Edge case: no clauses → trivially satisfiable.
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
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph has an independent set of size at least k.

    The instance follows the format defined in ``IndependentSet``.
    ``k`` may be non‑positive, in which case the answer is trivially True.
    """
    n = instance["n"]
    edges = [frozenset(e) for e in instance["edges"]]
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False

    # Build adjacency set for quick conflict checks.
    adj = [set() for _ in range(n)]
    for e in edges:
        u, v = tuple(e)
        adj[u].add(v)
        adj[v].add(u)

    # Check all subsets of size >= k (we can stop as soon as we find one).
    for size in range(k, n + 1):
        for subset in combinations(range(n), size):
            independent = True
            for i, u in enumerate(subset):
                for v in subset[i + 1 :]:
                    if v in adj[u]:
                        independent = False
                        break
                if not independent:
                    break
            if independent:
                return True
    return False


def random_sat_instance(max_vars: int = 3, max_clauses: int = 3, max_lits: int = 3) -> Dict[str, Any]:
    """Generate a random SAT instance respecting the validation rules.

    Variables are numbered from 1..m.  Literals are chosen uniformly from
    the allowed range; we also allow the possibility of an empty clause
    to test the unsatisfiable edge case.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # With small probability create an empty clause.
        if random.random() < 0.1:
            clauses.append([])
            continue
        lits_in_clause = random.randint(1, max_lits)
        clause: List[int] = []
        for _ in range(lits_in_clause):
            if m == 0:
                # No variables – we cannot create a non‑empty clause.
                continue
            var = random.randint(1, m)
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0

    for _ in range(200):
        sat_inst = random_sat_instance()
        # Validate the generated instance – should never raise.
        Sat.validate(sat_inst)
        sat_answer = sat_bruteforce(sat_inst)
        # Reduce and validate the target instance.
        indep_inst = reduce_instance(sat_inst)
        IndependentSet.validate(indep_inst)
        indep_answer = independent_set_bruteforce(indep_inst)
        tests_run += 1
        if sat_answer == indep_answer:
            tests_passed += 1
        else:
            # Print a diagnostic for debugging.
            print("Mismatch!", file=sys.stderr)
            print("SAT instance:", sat_inst, file=sys.stderr)
            print("SAT answer:", sat_answer, file=sys.stderr)
            print("Reduced instance:", indep_inst, file=sys.stderr)
            print("IS answer:", indep_answer, file=sys.stderr)

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

    # Also print the verdict for visibility.
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
