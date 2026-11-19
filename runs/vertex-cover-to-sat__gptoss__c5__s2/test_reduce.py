"""Automated tests for the VertexCover → SAT reduction.

The repository provides only validation functions for the two problems.
To check the correctness of ``reduce.py`` we implement tiny brute‑force
solvers for both problems and compare the answer on a large number of
randomly generated instances.

The test script is deliberately simple – it does not aim for exhaustive
coverage of all possible graphs, but it explores a wide range of small
graphs (n ≤ 4) and all reasonable values of ``k``.  For each instance we
  * compute the exact answer for VertexCover;
  * run the reduction to obtain a SAT instance;
  * compute the exact answer for the SAT instance;
  * assert that the two answers coincide.

If any discrepancy is found the script exits with a non‑zero status which
will cause the CI (and the verification step) to fail.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

from problems import VertexCover, Sat
from reduce import reduce


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a vertex cover of size at most k.

    The instance follows the ``VertexCover`` format.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    # Edge cases directly from the problem statement
    if k < 0:
        return False
    if not edges:
        return True  # empty graph always covered
    if k >= n:
        return True
    # Try all subsets up to size k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the CNF formula is satisfiable.

    The instance follows the ``Sat`` format.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Empty clause makes formula unsatisfiable
    for clause in clauses:
        if not clause:
            return False
    # No clauses => trivially satisfiable
    if not clauses:
        return True
    # Enumerate all assignments
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # index i -> var i+1
        ok = True
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
                ok = False
                break
        if ok:
            return True
    return False


def generate_random_instance(max_n: int = 4) -> dict:
    """Generate a random VertexCover instance with small size.

    ``n`` is chosen uniformly from 0..max_n.  All possible edges are considered
    and a random subset is taken.  ``k`` is chosen from -1..n+1 to hit edge
    cases.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for e in possible_edges:
        if random.choice([True, False]):
            edges.append(list(e))
    k = random.randint(-1, n + 1)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):  # enough random tests
        instance = generate_random_instance()
        # Validate source instance (will raise if malformed)
        VertexCover.validate(instance)
        vc_answer = vertex_cover_bruteforce(instance)
        sat_instance = reduce(instance)
        # Validate the produced SAT instance
        Sat.validate(sat_instance)
        sat_answer = sat_bruteforce(sat_instance)
        total += 1
        if vc_answer == sat_answer:
            passed += 1
        else:
            print("Discrepancy found!", file=sys.stderr)
            print("VertexCover instance:", json.dumps(instance, indent=2), file=sys.stderr)
            print("Expected (VC):", vc_answer, file=sys.stderr)
            print("Reduced SAT instance:", json.dumps(sat_instance, indent=2), file=sys.stderr)
            print("SAT result:", sat_answer, file=sys.stderr)
            sys.exit(1)
    # Write verdict.json
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

