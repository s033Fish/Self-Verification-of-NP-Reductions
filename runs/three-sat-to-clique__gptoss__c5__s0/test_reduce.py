"""Automated tests for the reduction from 3‑SAT to Clique.

The repository provides only validation functions for the two problems and
the reduction implementation.  In order to verify that the reduction is
correct we implement tiny brute‑force solvers for both source and target
problems and compare the answers on a collection of random instances.

The script generates a number of random 3‑SAT instances (with a small number
of variables and clauses so that exhaustive search is feasible), runs the
reduction, solves the resulting Clique instance, and checks that the answers
agree.  Finally it writes ``verdict.json`` containing the number of tests
executed, how many passed and a boolean ``verified`` flag.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import product, combinations
from typing import Dict, List

from problems import ThreeSat, Clique
from reduce import reduce as reduce_instance

# ---------------------------------------------------------------------------
# Brute‑force solvers


def solve_three_sat(instance: Dict) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance is assumed to be valid according to ``ThreeSat.validate``.
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
                if lit > 0:
                    clause_ok = clause_ok or val
                else:
                    clause_ok = clause_ok or (not val)
                if clause_ok:
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance: Dict) -> bool:
    """Return True iff the graph contains a clique of size at least ``k``.

    Exhaustively checks all subsets of vertices for small ``n``.
    """
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        edges.add(frozenset((u, v)))
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in combinations(range(n), size):
            all_edges = True
            for u, v in combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    all_edges = False
                    break
            if all_edges:
                return True
    return False

# ---------------------------------------------------------------------------
# Random instance generator for 3‑SAT


def random_three_sat(max_vars: int = 4, max_clauses: int = 4) -> Dict:
    """Generate a random 3‑SAT instance respecting the validation rules.

    ``max_vars`` and ``max_clauses`` bound the size to keep the search space
    small.  The function may return an instance with zero clauses.
    """
    num_clauses = random.randint(0, max_clauses)
    if num_clauses == 0:
        m = random.randint(0, max_vars)
    else:
        bound = max(max_vars, 3)
        m = random.randint(3, bound)
    clauses: List[List[int]] = []
    for _ in range(num_clauses):
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    instance = {"num_vars": m, "clauses": clauses}
    ThreeSat.validate(instance)
    return instance

# ---------------------------------------------------------------------------
# Test harness


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        total += 1
        src = random_three_sat()
        sat = solve_three_sat(src)
        try:
            tgt = reduce_instance(src)
        except Exception as e:
            print(f"Reduction raised an exception: {e}", file=sys.stderr)
            continue
        try:
            Clique.validate(tgt)
        except Exception as e:
            print(f"Reduced instance invalid: {e}", file=sys.stderr)
            continue
        clique_yes = solve_clique(tgt)
        if sat == clique_yes:
            passed += 1
        else:
            print("Mismatch found:")
            print("3‑SAT instance:", src)
            print("SAT answer:", sat)
            print("Clique instance:", tgt)
            print("Clique answer:", clique_yes)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
