"""Tests for the reduction from ThreeSat to ExactCover.

The repository provides only validation functions for the two problems.
This test module implements tiny brute‑force solvers for both problems and
exercises the ``reduce`` function on many random small instances.  For each
instance we check that:

1. The instance validates against the source problem definition.
2. The reduced instance validates against the target problem definition.
3. The answer of the source solver equals the answer of the target solver.

If every generated test passes we consider the reduction verified.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product
from typing import List, Dict, Any

import problems  # provides ThreeSat and ExactCover with .validate
import reduce


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for 3‑SAT.

    The instance format follows ``ThreeSat``: ``{"num_vars": m,
    "clauses": [[l1, l2, l3], ...]}``.  Literals are integers where a positive
    value means the variable is true and a negative value means false.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # iterate over all 2^m assignments
    for bits in product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
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


def solve_exact_cover(instance: Dict[str, Any]) -> bool:
    """Brute‑force exact‑cover solver.

    ``instance`` has keys ``universe_size`` and ``sets`` where each set is a
    list of distinct elements in ``0..u-1``.
    """
    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]

    # Pre‑compute which sets contain each element for quick lookup.
    element_to_sets: List[List[int]] = [[] for _ in range(u)]
    for idx, s in enumerate(sets):
        for e in s:
            element_to_sets[e].append(idx)

    used = [False] * u  # which elements are already covered
    chosen: List[int] = []

    def backtrack() -> bool:
        # Find first uncovered element
        try:
            e = used.index(False)
        except ValueError:
            # all covered
            return True
        for set_idx in element_to_sets[e]:
            s = sets[set_idx]
            # check if set is compatible (no already covered element)
            if any(used[x] for x in s):
                continue
            # choose it
            for x in s:
                used[x] = True
            chosen.append(set_idx)
            if backtrack():
                return True
            # undo
            chosen.pop()
            for x in s:
                used[x] = False
        return False

    return backtrack()


def random_three_sat(max_vars: int = 3, max_clauses: int = 3) -> Dict[str, Any]:
    """Generate a random 3‑SAT instance respecting the problem constraints.

    The generator may produce duplicate clauses – that is allowed by the
    specification.
    """
    m = random.randint(0, max_vars)
    n = random.randint(0, max_clauses)
    clauses: List[List[int]] = []
    for _ in range(n):
        if m < 3:
            continue
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    failures: List[Dict[str, Any]] = []

    for _ in range(200):
        src = random_three_sat()
        try:
            problems.ThreeSat.validate(src)
        except Exception:
            continue
        total += 1
        tgt = reduce.reduce(src)
        problems.ExactCover.validate(tgt)
        src_ans = solve_three_sat(src)
        tgt_ans = solve_exact_cover(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            failures.append({"src": src, "tgt": tgt, "src_ans": src_ans, "tgt_ans": tgt_ans})

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
    if failures:
        print("Failures:", file=sys.stderr)
        for f in failures:
            print(json.dumps(f, indent=2), file=sys.stderr)

if __name__ == "__main__":
    main()
