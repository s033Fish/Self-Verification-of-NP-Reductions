"""Automated tests for the SAT → 3‑SAT reduction.

The repository provides only validation logic for the source (Sat) and target
 (ThreeSat) problems.  To verify that ``reduce.py`` implements a correct
 polynomial‑time reduction we:

1. Implement tiny brute‑force solvers for SAT and 3‑SAT.
2. Generate a large number of random small instances (including edge cases).
3. For each instance compute the SAT answer, run ``reduce`` and compute the
   3‑SAT answer of the returned instance.
4. Record how many tests were run and how many passed.
5. Write a ``verdict.json`` file summarizing the result.

The script is intended to be executed directly (e.g. ``python test_reduce.py``)
by the reviewer harness.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Any

from problems import Sat, ThreeSat
from reduce import reduce as reduce_instance


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in :class:`Sat`.  This function
    enumerates all assignments for ``num_vars`` (which is small in the tests).
    """
    Sat.validate(instance)
    n = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # Empty clause list => trivially satisfiable
    for mask in range(1 << n):
        ok = True
        for clause in clauses:
            # Empty clause is unsatisfiable
            if not clause:
                ok = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool(mask & (1 << var))
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


def three_sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for 3‑SAT instances.

    The format matches :class:`ThreeSat`.  All clauses have exactly three
    literals, but we do not rely on that for correctness.
    """
    ThreeSat.validate(instance)
    n = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for mask in range(1 << n):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool(mask & (1 << var))
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


def random_sat_instance(max_vars: int = 4, max_clauses: int = 5) -> Dict[str, Any]:
    """Generate a random SAT instance respecting the specification.

    The generator includes edge cases such as empty clause lists, empty
    clauses, duplicate literals and tautologies.
    """
    num_vars = random.randint(0, max_vars)
    clause_count = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(clause_count):
        # Randomly decide clause length (0..num_vars+2 to allow duplicates)
        length = random.randint(0, max(0, num_vars + 2))
        clause: List[int] = []
        for _ in range(length):
            if num_vars == 0:
                continue
            var = random.randint(1, num_vars)
            sign = random.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_sat_instance()
        sat_ans = sat_bruteforce(inst)
        reduced = reduce_instance(inst)
        three_sat_ans = three_sat_bruteforce(reduced)
        total += 1
        if sat_ans == three_sat_ans:
            passed += 1
        else:
            print("FAILURE", file=sys.stderr)
            print(json.dumps({"instance": inst, "sat_ans": sat_ans, "reduced": reduced, "three_sat_ans": three_sat_ans}), file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
