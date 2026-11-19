"""Tests for the reduction from 3‑SAT to Independent Set.

The repository provides a ``reduce`` function but no solvers.  To verify the
reduction we implement tiny brute‑force solvers for both source and target
problems and compare their answers on a collection of randomly generated
instances.

The test suite records how many instances were generated and how many passed.
It also writes a ``verdict.json`` file as required by the task description.
"""

from __future__ import annotations

import json
import random
import itertools
import sys
from pathlib import Path
import unittest

# Import the problem definitions and the reduction.
import problems  # provides ThreeSat and IndependentSet with .validate
from reduce import reduce as reduce_instance


def brute_three_sat(instance: dict) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance format follows ``ThreeSat``: ``{"num_vars": m, "clauses": [...]}``.
    """
    m: int = instance["num_vars"]
    clauses: list[list[int]] = instance["clauses"]
    # Enumerate all assignments of m variables (0 = false, 1 = true).
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1  # variables are 1‑based
                val = (bits >> var) & 1
                # literal is true if (lit > 0 and val == 1) or (lit < 0 and val == 0)
                if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def brute_independent_set(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size >= k.

    Instance format follows ``IndependentSet``: ``{"n": n, "edges": [...], "k": k}``.
    """
    n: int = instance["n"]
    edges: list[list[int]] = instance["edges"]
    k: int = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False

    # Build adjacency matrix for quick checks.
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True

    # Check all subsets of size >= k (we stop early when we find one).
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            independent = True
            for i, u in enumerate(combo):
                for v in combo[i + 1 :]:
                    if adj[u][v]:
                        independent = False
                        break
                if not independent:
                    break
            if independent:
                return True
    return False


def random_three_sat_instance(max_vars: int = 4, max_clauses: int = 4) -> dict:
    """Generate a random valid 3‑SAT instance.

    The generator respects all constraints of ``ThreeSat.validate``.
    """
    # Choose number of variables. For formulas with clauses we need at least 3 vars.
    m = random.randint(0, max_vars)
    # Number of clauses may be zero.
    num_clauses = random.randint(0, max_clauses)
    if num_clauses > 0 and m < 3:
        m = random.randint(3, max_vars)
    clauses: list[list[int]] = []
    for _ in range(num_clauses):
        # pick 3 distinct variables
        vars_ = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


class ReductionTest(unittest.TestCase):
    def test_random_instances(self):
        total = 200
        passed = 0
        for _ in range(total):
            instance = random_three_sat_instance()
            # Validate source instance (should not raise).
            problems.ThreeSat.validate(instance)
            sat = brute_three_sat(instance)
            reduced = reduce_instance(instance)
            # Validate target instance.
            problems.IndependentSet.validate(reduced)
            indep = brute_independent_set(reduced)
            self.assertEqual(sat, indep)
            passed += 1
        # Write verdict.
        verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
        Path("verdict.json").write_text(json.dumps(verdict))

if __name__ == "__main__":
    # Run the unittest and ensure the script exits with non‑zero on failure.
    result = unittest.main(argv=[sys.argv[0]], exit=False)
    # If there were failures, mark verification as false.
    if not result.result.wasSuccessful():
        verdict = {"verified": False, "tests_run": result.result.testsRun, "tests_passed": result.result.testsRun - len(result.result.failures) - len(result.result.errors)}
        Path("verdict.json").write_text(json.dumps(verdict))
        sys.exit(1)
