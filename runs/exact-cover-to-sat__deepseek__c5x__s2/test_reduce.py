"""Automated tests for the ExactCover → SAT reduction.

The repository provides only validation functions for the two problems.
To verify the correctness of ``reduce.py`` we implement tiny brute‑force
solvers for Exact Cover and SAT, generate a large number of random small
instances, apply the reduction and compare the answers.

If every generated instance yields the same answer before and after the
reduction we consider the reduction verified.  The script prints a JSON
object matching the required ``verdict.json`` format.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict

import problems  # the provided module containing ExactCover and Sat
from reduce import reduce as reduce_instance


def exact_cover_bruteforce(instance: Dict) -> bool:
    """Return True iff the Exact Cover instance is a YES instance.

    The universe size is small in the tests, so we can enumerate all
    subsets of the given sets.
    """
    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    n = len(sets)
    masks = []
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        masks.append(mask)
    full_mask = (1 << u) - 1
    for choose in range(1 << n):
        union = 0
        ok = True
        for i in range(n):
            if choose >> i & 1:
                if union & masks[i]:
                    ok = False
                    break
                union |= masks[i]
        if ok and union == full_mask:
            return True
    return False


def sat_bruteforce(instance: Dict) -> bool:
    """Return True iff the SAT instance is satisfiable (brute force)."""
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for assignment in product([False, True], repeat=m):
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_random_instance(max_u: int, max_sets: int) -> Dict:
    """Generate a random ExactCover instance.

    * universe size ``u`` is chosen uniformly in ``0..max_u``.
    * number of sets ``s`` is chosen uniformly in ``0..max_sets``.
    * each set is created by independently including each element with
      probability 0.5.  Empty sets and duplicate sets are allowed, matching
      the problem definition.
    """
    u = random.randint(0, max_u)
    s = random.randint(0, max_sets)
    sets = []
    for _ in range(s):
        subset = [e for e in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)
    total_tests = 0
    passed = 0
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[0]]},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0, 1], []]},
    ]
    for inst in edge_cases:
        total_tests += 1
        try:
            problems.ExactCover.validate(inst)
        except Exception:
            continue
        ec_answer = exact_cover_bruteforce(inst)
        reduced = reduce_instance(inst)
        problems.Sat.validate(reduced)
        sat_answer = sat_bruteforce(reduced)
        if ec_answer == sat_answer:
            passed += 1
        else:
            print("EDGE FAILURE", inst, file=sys.stderr)
    for _ in range(200):
        total_tests += 1
        inst = generate_random_instance(max_u=4, max_sets=5)
        problems.ExactCover.validate(inst)
        ec_answer = exact_cover_bruteforce(inst)
        reduced = reduce_instance(inst)
        problems.Sat.validate(reduced)
        sat_answer = sat_bruteforce(reduced)
        if ec_answer == sat_answer:
            passed += 1
        else:
            print("FAILURE instance:", inst, file=sys.stderr)
            print("ExactCover answer", ec_answer, "Sat answer", sat_answer, file=sys.stderr)
    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
    sys.exit(0 if verdict["verified"] else 1)

if __name__ == "__main__":
    main()
