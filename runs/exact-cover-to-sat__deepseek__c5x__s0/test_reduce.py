"""Tests for the ExactCover to SAT reduction.

The repository provides only validation functions for the two problems and a
``reduce`` implementation.  To verify the reduction we implement brute‑force
solvers for both Exact Cover and SAT based directly on the problem
descriptions.  For a collection of small random instances we check that the
answer to the source instance matches the answer to the reduced SAT instance.

If all checks pass we consider the reduction verified.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product

import problems
from reduce import reduce as reduction


def exact_cover_solver(instance: dict) -> bool:
    """Return True iff the Exact Cover instance is a yes‑instance.

    Brute‑force over all subsets of the given sets.  The universe size is
    ``u`` and there are ``n`` sets.  We check each selection of sets whether
    they are pairwise disjoint and cover the whole universe.
    """
    problems.ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    set_frozens = [frozenset(s) for s in sets]
    for mask in range(1 << n):
        covered: set[int] = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                if set_frozens[i] & covered:
                    ok = False
                    break
                covered.update(set_frozens[i])
        if not ok:
            continue
        if u == 0:
            return True
        if covered == set(range(u)):
            return True
    return False


def sat_solver(instance: dict) -> bool:
    """Return True iff the SAT instance is satisfiable (brute force)."""
    problems.Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in product([False, True], repeat=m):
        all_ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                all_ok = False
                break
        if all_ok:
            return True
    return False


def generate_random_instance(max_universe: int, max_sets: int, max_set_size: int) -> dict:
    """Create a random Exact Cover instance within the given bounds."""
    u = random.randint(0, max_universe)
    n = random.randint(0, max_sets)
    sets = []
    for _ in range(n):
        size = random.randint(0, max_set_size)
        if u > 0:
            size = min(size, u)
            subset = random.sample(range(u), k=size)
        else:
            subset = []
        sets.append(subset)
    return {"universe_size": u, "sets": sets}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    mismatches = []
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0, 1]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0], [0, 1]]},
    ]
    for instance in edge_cases:
        try:
            problems.ExactCover.validate(instance)
        except Exception:
            continue
        tests_run += 1
        src_ans = exact_cover_solver(instance)
        red = reduction(instance)
        try:
            problems.Sat.validate(red)
        except Exception as e:
            mismatches.append((instance, "invalid reduction", str(e)))
            continue
        tgt_ans = sat_solver(red)
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            mismatches.append((instance, src_ans, tgt_ans))
    for _ in range(200):
        inst = generate_random_instance(max_universe=4, max_sets=5, max_set_size=4)
        try:
            problems.ExactCover.validate(inst)
        except Exception:
            continue
        tests_run += 1
        src_ans = exact_cover_solver(inst)
        red = reduction(inst)
        try:
            problems.Sat.validate(red)
        except Exception as e:
            mismatches.append((inst, "invalid reduction", str(e)))
            continue
        tgt_ans = sat_solver(red)
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            mismatches.append((inst, src_ans, tgt_ans))
    verified = len(mismatches) == 0
    verdict = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    print(json.dumps(verdict, indent=2))
    if not verified:
        print("Mismatches:", file=sys.stderr)
        for mis in mismatches:
            print(mis, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
