"""Tests for the reduction from 3‑SAT to 3‑Coloring.

The repository provides only validation functions for the two problems.
This test module implements straightforward brute‑force solvers for both
problems, generates a number of small random instances, runs the supplied
``reduce`` function and checks that:

1. The reduction output is a valid 3‑Coloring instance.
2. The answer (yes/no) of the original 3‑SAT instance matches the answer of
   the produced 3‑Coloring instance.

The result of the test run is written to ``verdict.json`` in the required
format.
"""

from __future__ import annotations

import json
import random
from itertools import product
from pathlib import Path

import problems
from reduce import reduce as reduce_instance


def three_sat_solver(instance: dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    Returns ``True`` iff there exists an assignment to the variables that
    satisfies all clauses.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    satisfied = True
                if lit < 0 and not val:
                    satisfied = True
                if satisfied:
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def three_coloring_solver(instance: dict) -> bool:
    """Backtracking solver for 3‑Coloring.

    The naive ``product`` approach quickly becomes infeasible for graphs with
    more than a dozen vertices.  A simple depth‑first backtracking with early
    pruning is sufficient for the tiny graphs generated in the tests.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    adjacency: list[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    colours: list[int | None] = [None] * n
    def backtrack(v: int) -> bool:
        if v == n:
            return True
        for c in range(3):
            if all(colours[nb] != c for nb in adjacency[v] if colours[nb] is not None):
                colours[v] = c
                if backtrack(v + 1):
                    return True
                colours[v] = None
        return False
    return backtrack(0)


def random_three_sat_instance(max_vars: int = 4, max_clauses: int = 5) -> dict:
    """Generate a random 3‑SAT instance respecting the problem constraints.

    The number of variables is chosen uniformly from ``0..max_vars``.  For
    ``num_vars`` less than 3 we generate zero clauses because a clause would
    require three distinct variables.
    """
    m = random.randint(0, max_vars)
    clauses = []
    if m >= 3:
        possible_vars = list(range(1, m + 1))
        num_clauses = random.randint(0, max_clauses)
        for _ in range(num_clauses):
            vars_in_clause = random.sample(possible_vars, 3)
            clause = []
            for v in vars_in_clause:
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        instance = random_three_sat_instance()
        problems.ThreeSat.validate(instance)
        reduced = reduce_instance(instance)
        problems.ThreeColoring.validate(reduced)
        sat_answer = three_sat_solver(instance)
        col_answer = three_coloring_solver(reduced)
        total += 1
        if sat_answer == col_answer:
            passed += 1
        else:
            print("Mismatch found:")
            print("SAT instance:", json.dumps(instance))
            print("SAT answer:", sat_answer)
            print("Reduced instance:", json.dumps(reduced))
            print("Coloring answer:", col_answer)
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
