"""Automated tests for the reduction from 3‑SAT to Dominating Set.

The repository provides a ``reduce`` function but no solvers.  This file
contains simple exhaustive solvers for both problems and uses them to
verify that ``reduce`` preserves the answer on a large collection of small
random instances.

The script is intended to be run directly (e.g. ``python -m pytest`` or
``python test_reduce.py``).  It creates a ``verdict.json`` file with the
required fields ``verified``, ``tests_run`` and ``tests_passed``.
"""

from __future__ import annotations

import json
import random
import itertools
from pathlib import Path
from typing import List, Dict

from problems import ThreeSat, DominatingSet
from reduce import reduce as reduce_instance


def solve_three_sat(instance: Dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    Returns ``True`` iff there exists an assignment to the variables that
    satisfies all clauses.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # enumerate all 2^m assignments; represent as bitmask where bit i (0‑based)
    # indicates variable i+1 is True.
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1  # 1 if true
                if lit > 0 and val == 1:
                    clause_ok = True
                if lit < 0 and val == 0:
                    clause_ok = True
                if clause_ok:
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_dominating_set(instance: Dict) -> bool:
    """Brute‑force solver for Dominating Set.

    Returns ``True`` iff there exists a dominating set of size at most ``k``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True

    # adjacency list including self (dominated if in set)
    adj: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    vertices = range(n)
    # iterate over subsets up to size k
    for size in range(k + 1):
        for combo in itertools.combinations(vertices, size):
            dominated = set(combo)
            for v in combo:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def random_three_sat(max_vars: int = 4, max_clauses: int = 5) -> Dict:
    """Generate a random 3‑SAT instance respecting the problem constraints."""
    m = random.randint(0, max_vars)
    # ensure at least 3 variables if there are clauses (as per spec)
    has_clauses = random.choice([True, False])
    if has_clauses and m < 3:
        m = random.randint(3, max_vars)
    num_clauses = random.randint(0, max_clauses) if has_clauses else 0
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        # pick three distinct variables
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    for _ in range(200):  # enough random tests for confidence
        src = random_three_sat()
        # Validate source (should not raise)
        ThreeSat.validate(src)
        src_ans = solve_three_sat(src)
        tgt = reduce_instance(src)
        # Validate target (reduce does this already, but double‑check)
        DominatingSet.validate(tgt)
        tgt_ans = solve_dominating_set(tgt)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            # Print the counter‑example for debugging (optional)
            print("Counter‑example found:")
            print(json.dumps(src, indent=2))
            print(json.dumps(tgt, indent=2))
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

