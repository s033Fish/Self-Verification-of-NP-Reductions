"""Test the SAT-to-Clique reduction.

The repository provides only validation for the two problems and a reduction
function. This test script implements tiny brute‑force solvers for SAT and
Clique and then checks that for many random small instances the answer of the
reduced instance matches the original answer.

The script produces a ``verdict.json`` file with the required fields:

* ``verified`` – true iff all tests passed.
* ``tests_run`` – total number of random instances generated.
* ``tests_passed`` – number of instances where the reduction preserved the
  answer.

The script is intended to be executed from the repository root.
"""

from __future__ import annotations

import json
import random
import itertools
from pathlib import Path

from problems import Sat, Clique
from reduce import reduce


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in ``Sat``: ``{"num_vars": m,
    "clauses": [[lit, ...], ...]}``.  ``lit`` is a signed integer where the
    absolute value is the variable index (1‑based) and the sign indicates the
    polarity.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: empty clause makes formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # Edge case: no clauses – trivially satisfiable.
    if not clauses:
        return True
    for assignment in itertools.product([False, True], repeat=m):
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


def clique_bruteforce(instance: dict) -> bool:
    """Return True iff the graph contains a clique of size at least k.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    # Edge cases handled by brute force as well.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = range(n)
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            if all(frozenset((a, b)) in edges for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def random_sat_instance(max_vars: int = 4, max_clauses: int = 4, max_lits: int = 3) -> dict:
    """Generate a random SAT instance respecting the validation rules.
    """
    num_vars = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        clause_len = random.randint(0, max_lits)
        clause = []
        for _ in range(clause_len):
            if num_vars == 0:
                continue
            var = random.randint(1, num_vars)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 200
    passed = 0
    for _ in range(total):
        sat_inst = random_sat_instance()
        Sat.validate(sat_inst)
        sat_ans = sat_bruteforce(sat_inst)
        clique_inst = reduce(sat_inst)
        Clique.validate(clique_inst)
        clique_ans = clique_bruteforce(clique_inst)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch!", sat_inst, sat_ans, clique_inst, clique_ans)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
