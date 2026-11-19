"""Automated tests for the SAT → 3‑SAT reduction.

The repository provides only validation helpers for the two problems.  This
test suite implements brute‑force solvers for SAT and 3‑SAT, generates a large
number of small random instances of SAT, reduces each instance with the
provided ``reduce`` function and checks that the answers agree.

If all generated instances behave correctly we write ``verdict.json`` with
``verified: true``.  Any mismatch leads to ``verified: false``.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict, Any

from problems import Sat, ThreeSat
from reduce import reduce as reduce_instance


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in :class:`Sat`.  We simply try
    every assignment of the ``num_vars`` variables.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Enumerate assignments as a tuple of booleans of length m (1‑based).
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # Empty clause is unsatisfiable.
            if not clause:
                ok = False
                break
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1  # zero‑based index
                val = bits[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def threesat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for 3‑SAT.

    The format is defined in :class:`ThreeSat`.  All clauses have exactly three
    literals on distinct variables, but we do not rely on that property – we
    simply evaluate the formula.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def random_sat_instance(max_vars: int = 4, max_clauses: int = 4) -> Dict[str, Any]:
    """Create a random SAT instance.

    ``max_vars`` and ``max_clauses`` bound the size to keep the brute‑force
    solver tractable.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # Clause length can be 0..(2*m) (allow duplicates)
        length = random.randint(0, max(0, 2 * m))
        clause = []
        for _ in range(length):
            if m == 0:
                # No variables, but we may still create an empty clause.
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
    for _ in range(500):  # enough random tests for reasonable confidence
        inst = random_sat_instance()
        # Validate the original instance (should never raise).
        Sat.validate(inst)
        sat_ans = sat_bruteforce(inst)
        reduced = reduce_instance(inst)
        # Validate the reduced instance.
        ThreeSat.validate(reduced)
        threesat_ans = threesat_bruteforce(reduced)
        total += 1
        if sat_ans == threesat_ans:
            passed += 1
        else:
            # Print a minimal example for debugging.
            print("Mismatch detected!", file=sys.stderr)
            print("Original SAT instance:", json.dumps(inst), file=sys.stderr)
            print("Reduced 3‑SAT instance:", json.dumps(reduced), file=sys.stderr)
            print("SAT answer:", sat_ans, "3‑SAT answer:", threesat_ans, file=sys.stderr)
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

