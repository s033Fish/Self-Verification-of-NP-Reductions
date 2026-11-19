"""Test the reduction from SAT to Independent Set.

The repository provides only validation functions for the two problems.
We implement tiny brute‑force solvers for both problems and then generate
random small SAT instances. For each instance we:

1. Validate the original SAT instance.
2. Compute the SAT answer with ``sat_bruteforce``.
3. Apply ``reduce`` to obtain an Independent‑Set instance.
4. Validate the produced Independent‑Set instance.
5. Compute the Independent‑Set answer with ``independent_set_bruteforce``.
6. Verify that the two answers are identical.

The script counts the total number of tests run and the number passed and
writes ``verdict.json`` in the repository root. ``verified`` is true only
if every test passes.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from pathlib import Path

import problems  # provides Sat.validate and IndependentSet.validate
from reduce import reduce as reduce_instance


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance conforms to the format described in ``problems.Sat``.
    ``num_vars`` may be zero. ``clauses`` is a list of lists of integers.
    """
    num_vars: int = instance["num_vars"]
    clauses: list[list[int]] = instance["clauses"]

    # Any empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # No clauses → trivially satisfiable.
    if not clauses:
        return True

    for bits in product([False, True], repeat=num_vars):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
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


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size >= k.

    The instance follows ``problems.IndependentSet`` format.
    """
    n: int = instance["n"]
    edges: list[list[int]] = instance["edges"]
    k: int = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    vertices = range(n)
    for size in range(k, n + 1):
        for subset in combinations(vertices, size):
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


def random_sat_instance(max_vars: int, max_clauses: int, max_lits_per_clause: int) -> dict:
    """Generate a random SAT instance respecting validation rules."""
    num_vars = random.randint(0, max_vars)
    clauses: list[list[int]] = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        clause_len = random.randint(0, max_lits_per_clause)
        clause: list[int] = []
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
    total = 0
    passed = 0
    failures = []

    for _ in range(200):
        sat_inst = random_sat_instance(max_vars=4, max_clauses=4, max_lits_per_clause=3)
        try:
            problems.Sat.validate(sat_inst)
        except Exception:
            continue
        total += 1
        sat_ans = sat_bruteforce(sat_inst)
        indep_inst = reduce_instance(sat_inst)
        try:
            problems.IndependentSet.validate(indep_inst)
        except Exception as exc:
            failures.append({"type": "validation", "instance": sat_inst, "error": str(exc)})
            continue
        indep_ans = independent_set_bruteforce(indep_inst)
        if sat_ans == indep_ans:
            passed += 1
        else:
            failures.append(
                {
                    "type": "mismatch",
                    "sat": sat_inst,
                    "indep": indep_inst,
                    "sat_ans": sat_ans,
                    "indep_ans": indep_ans,
                }
            )
    verdict = {
        "verified": total == passed and total > 0,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))
    if failures:
        print("\nFailures:", file=sys.stderr)
        for f in failures:
            print(json.dumps(f, indent=2), file=sys.stderr)

if __name__ == "__main__":
    main()
