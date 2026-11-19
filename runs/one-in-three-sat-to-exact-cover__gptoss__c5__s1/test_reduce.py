"""Tests for the reduction from OneInThreeSat to ExactCover.

The repository provides a ``reduce`` function that maps a source instance
to a target instance.  The reduction is considered correct if the answer
(`yes`/`no`) of the source instance equals the answer of the produced target
instance.

Since ``problems.py`` only contains validation helpers, we implement tiny
brute‑force solvers for both problems based on the definitions in the
docstrings.  The tests generate a number of random small instances of the
source problem, run the reduction, and compare the answers.

The script exits with status 0 if all tests pass and prints a JSON object
containing the verification result, which will be written to ``verdict.json``
by the surrounding harness.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations
from typing import List, Dict, Any

from problems import OneInThreeSat, ExactCover
from reduce import reduce as reduce_instance


def solve_one_in_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for OneInThreeSat.

    Returns ``True`` iff there exists an assignment of truth values to the
    variables such that exactly one variable in each clause is true.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_cnt = sum(bits[var - 1] for var in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for ExactCover.

    Returns ``True`` iff there exists a sub‑collection of the given sets that
    forms an exact cover of the universe.
    """
    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    set_frozens = [frozenset(s) for s in sets]
    n = len(set_frozens)
    for r in range(n + 1):
        for combo in combinations(range(n), r):
            covered = set()
            disjoint = True
            for idx in combo:
                s = set_frozens[idx]
                if covered & s:
                    disjoint = False
                    break
                covered |= s
            if disjoint and covered == set(range(u)):
                return True
    return False


def generate_random_one_in_three_instance(max_vars: int = 5, max_clauses: int = 5) -> Dict[str, Any]:
    """Generate a random valid OneInThreeSat instance.

    The numbers are kept small to keep the brute‑force solver fast.
    """
    m = random.randint(0, max_vars)
    if m > 0 and m < 3:
        m = 3
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        if m == 0:
            break
        vars_choice = random.sample(range(1, m + 1), 3)
        random.shuffle(vars_choice)
        clauses.append(vars_choice)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    for _ in range(200):
        src = generate_random_one_in_three_instance()
        OneInThreeSat.validate(src)
        src_answer = solve_one_in_three_sat(src)
        tgt = reduce_instance(src)
        ExactCover.validate(tgt)
        tgt_answer = solve_exact_cover(tgt)
        tests_run += 1
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            print("Mismatch!", src, src_answer, tgt, tgt_answer, file=sys.stderr)
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
    ]
    for src in edge_cases:
        OneInThreeSat.validate(src)
        src_answer = solve_one_in_three_sat(src)
        tgt = reduce_instance(src)
        ExactCover.validate(tgt)
        tgt_answer = solve_exact_cover(tgt)
        tests_run += 1
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            print("Edge mismatch!", src, src_answer, tgt, tgt_answer, file=sys.stderr)
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

