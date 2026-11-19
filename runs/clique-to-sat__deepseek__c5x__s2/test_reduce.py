"""Automated tests for the Clique → SAT reduction.

The repository provides only validation helpers for the problem instances
but no solvers.  This test suite implements simple brute‑force solvers for the
Clique and SAT problems and checks that the reduction defined in ``reduce.py``
preserves the answer for a large number of small random instances.

The script is deliberately self‑contained and does not rely on any external
libraries – it only uses the standard library.  It is executed by the
verification harness after the patch is applied.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

# Import the reduction implementation.
from reduce import reduce as reduce_instance


def brute_clique(instance: dict) -> bool:
    """Return True iff the Clique instance has a clique of size at least k.

    The instance format follows the specification in ``problems.py``:
    ``{"n": int, "edges": [[u, v], ...], "k": int}``.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    # Edge cases from the specification.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    vertices = list(range(n))
    # Check all subsets of size >= k (we can stop early when we find one).
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Verify that every pair is an edge.
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def brute_sat(instance: dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Instance format: ``{"num_vars": m, "clauses": [[lit, ...], ...]}`` where
    literals are integers (+v for true, -v for false).  An empty clause makes
    the formula unsatisfiable; a formula with no clauses is trivially
    satisfiable.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Early detection of an empty clause.
    if any(len(clause) == 0 for clause in clauses):
        return False
    # No clauses -> satisfiable.
    if not clauses:
        return True

    # Enumerate all possible assignments.
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_random_instance() -> dict:
    """Generate a random Clique instance with very small parameters.

    To keep the brute‑force SAT solver tractable we restrict the size:
    * ``n`` is chosen from 0..4.
    * ``k`` is chosen from -1..4, ensuring ``k * n`` never exceeds 12.
    This still covers all edge‑case categories (negative, zero, >n) while
    keeping the search space manageable.
    """
    n = random.randint(0, 4)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges: list[list[int]] = []
    for u, v in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, 4)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    for _ in range(200):
        instance = generate_random_instance()
        total += 1
        ans_clique = brute_clique(instance)
        reduced = reduce_instance(instance)
        ans_sat = brute_sat(reduced)
        if ans_clique == ans_sat:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print(json.dumps({"instance": instance, "reduced": reduced, "clique": ans_clique, "sat": ans_sat}), file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    sys.exit(0 if verdict["verified"] else 1)

if __name__ == "__main__":
    main()
