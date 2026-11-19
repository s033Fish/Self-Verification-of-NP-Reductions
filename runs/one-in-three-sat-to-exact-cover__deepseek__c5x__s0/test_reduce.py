"""Automated tests for the reduction from OneInThreeSat to ExactCover.

The repository provides only validation functions for the two problems and a
reduction implementation.  To verify the reduction we implement brute‑force
solvers for both source and target problems and compare their answers on a
large collection of small, randomly generated instances.

The script is executed by the evaluation harness; it creates ``verdict.json``
containing the number of tests run, the number passed and a boolean ``verified``
field that is true only if every test succeeded.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations, combinations as comb
from pathlib import Path

# Import the problem definitions and the reduction implementation.
from problems import OneInThreeSat, ExactCover
from reduce import reduce as reduce_instance


def solve_one_in_three(instance: dict) -> bool:
    """Brute‑force solver for the positive 1‑in‑3‑SAT problem.

    Returns True iff there exists an assignment of the ``num_vars`` variables
    such that each clause contains exactly one true variable.
    """
    m = instance["num_vars"]
    clauses: list[list[int]] = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            true_count = 0
            for var in clause:
                if bits & (1 << (var - 1)):
                    true_count += 1
            if true_count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: dict) -> bool:
    """Brute‑force solver for Exact Cover.

    Returns True iff a sub‑collection of the given sets forms an exact cover
    of the universe ``0..u-1``.
    """
    u = instance["universe_size"]
    sets: list[list[int]] = instance["sets"]
    n_sets = len(sets)
    set_objs = [frozenset(s) for s in sets]
    from itertools import combinations
    for r in range(n_sets + 1):
        for combo in combinations(range(n_sets), r):
            covered: set[int] = set()
            valid = True
            for idx in combo:
                s = set_objs[idx]
                if covered & s:
                    valid = False
                    break
                covered |= s
            if not valid:
                continue
            if len(covered) == u:
                return True
    return False


def generate_random_one_in_three_instance(max_vars: int = 4, max_clauses: int = 4) -> dict:
    """Generate a random positive 1‑in‑3‑SAT instance.

    * ``max_vars`` – maximum number of variables (inclusive).
    * ``max_clauses`` – maximum number of clauses (inclusive).
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        var_range = max(m, 3)
        clause = random.sample(range(1, var_range + 1), 3)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    failures = []

    # Exhaustive small instances
    for m in range(0, 4):
        var_pool = list(range(1, max(m, 3) + 1))
        possible_clauses = list(combinations(var_pool, 3))
        for num_clauses in range(0, 3):
            for clause_selection in product(possible_clauses, repeat=num_clauses):
                instance = {"num_vars": m, "clauses": [list(c) for c in clause_selection]}
                try:
                    OneInThreeSat.validate(instance)
                except Exception:
                    continue
                src_ans = solve_one_in_three(instance)
                tgt_instance = reduce_instance(instance)
                ExactCover.validate(tgt_instance)
                tgt_ans = solve_exact_cover(tgt_instance)
                tests_run += 1
                if src_ans == tgt_ans:
                    tests_passed += 1
                else:
                    failures.append({"instance": instance, "src": src_ans, "tgt": tgt_ans})

    # Random tests
    for _ in range(200):
        instance = generate_random_one_in_three_instance()
        try:
            OneInThreeSat.validate(instance)
        except Exception as e:
            failures.append({"instance": instance, "error": str(e)})
            continue
        src_ans = solve_one_in_three(instance)
        tgt_instance = reduce_instance(instance)
        try:
            ExactCover.validate(tgt_instance)
        except Exception as e:
            failures.append({"instance": instance, "tgt_error": str(e)})
            continue
        tgt_ans = solve_exact_cover(tgt_instance)
        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append({"instance": instance, "src": src_ans, "tgt": tgt_ans})

    verified = tests_run == tests_passed
    verdict = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    if not verified:
        print("\nFailures (first 5):", file=sys.stderr)
        for f in failures[:5]:
            print(json.dumps(f, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
