"""Tests for the reduction from ThreeSat to VertexCover.

The script implements brute‑force solvers for both problems based on the
definitions in ``problems.py`` and then checks that for a large collection of
small random instances the answer of the reduced VertexCover instance matches
the answer of the original ThreeSat instance.

The verification result is written to ``verdict.json`` as required by the task
description.
"""

from __future__ import annotations

import json
import itertools
import random
import sys
from pathlib import Path

# Import the problem definitions and the reduction function.
import problems  # noqa: E402  (import after stdlib)
from reduce import reduce as reduce_instance  # noqa: E402


def three_sat_bruteforce(instance: dict) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance follows the format defined by ``ThreeSat``.  We simply try
    every possible assignment of the ``num_vars`` variables.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Iterate over all 2^m assignments represented as bit masks.
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            # Clause is satisfied if any literal evaluates to True.
            lit_true = False
            for lit in clause:
                var = abs(lit) - 1  # zero‑based index
                val = bool(mask & (1 << var))
                if lit > 0:
                    lit_true = lit_true or val
                else:
                    lit_true = lit_true or (not val)
                if lit_true:
                    break
            if not lit_true:
                ok = False
                break
        if ok:
            return True
    return False


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a vertex cover of size at most ``k``.

    Uses a simple recursive branching algorithm (choose an uncovered edge and
    branch on including one of its endpoints).  This is exponential but fast
    enough for the small graphs generated in the tests.
    """
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def search(frozen_edges: frozenset[tuple[int, int]], remaining_k: int) -> bool:
        if remaining_k < 0:
            return False
        if not frozen_edges:
            return True
        u, v = next(iter(frozen_edges))
        # Branch on u
        edges_without_u = frozenset(e for e in frozen_edges if u not in e)
        if search(edges_without_u, remaining_k - 1):
            return True
        # Branch on v
        edges_without_v = frozenset(e for e in frozen_edges if v not in e)
        if search(edges_without_v, remaining_k - 1):
            return True
        return False

    return search(frozenset(edges), k)


def generate_random_three_sat(max_vars: int = 4, max_clauses: int = 4) -> dict:
    """Generate a random well‑formed 3‑SAT instance.

    The generator respects the constraints from ``ThreeSat.validate`` – each
    clause contains three distinct variables and no clause contains both a
    variable and its negation.
    """
    m = random.randint(0, max_vars)
    # If we generate any clauses we need at least 3 variables.
    if m < 3:
        clauses: list[list[int]] = []
    else:
        num_clauses = random.randint(0, max_clauses)
        clauses = []
        for _ in range(num_clauses):
            vars_in_clause = random.sample(range(1, m + 1), 3)
            clause = []
            for v in vars_in_clause:
                sign = random.choice([1, -1])
                clause.append(sign * v)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    # Exhaustively test small sizes and also a bunch of random instances.
    for m in range(0, 4):
        for _ in range(20):
            inst = generate_random_three_sat(max_vars=m, max_clauses=3)
            problems.ThreeSat.validate(inst)
            reduced = reduce_instance(inst)
            problems.VertexCover.validate(reduced)
            ans_src = three_sat_bruteforce(inst)
            ans_tgt = vertex_cover_bruteforce(reduced)
            total += 1
            if ans_src == ans_tgt:
                passed += 1
            else:
                print("Mismatch!", inst, reduced, ans_src, ans_tgt, file=sys.stderr)
    for _ in range(200):
        inst = generate_random_three_sat(max_vars=5, max_clauses=5)
        problems.ThreeSat.validate(inst)
        reduced = reduce_instance(inst)
        problems.VertexCover.validate(reduced)
        ans_src = three_sat_bruteforce(inst)
        ans_tgt = vertex_cover_bruteforce(reduced)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ans_src, ans_tgt, file=sys.stderr)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
