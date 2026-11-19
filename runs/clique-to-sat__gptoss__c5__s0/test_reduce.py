"""Test suite for the Clique → SAT reduction.

The goal is to verify that ``reduce`` produces a SAT instance that is
equivalent to the original Clique instance.  We implement straightforward
brute‑force solvers for both problems (exponential but fine for tiny
instances) and compare the answers on a exhaustive set of small graphs.

The script is intended to be run directly.  It prints a short summary and
exits with status 0.  The surrounding harness will read ``verdict.json`` to
determine whether the reduction is verified.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import Clique, Sat, InvalidInstance
from reduce import reduce as reduce_instance


def clique_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a clique of size at least k.

    The instance is assumed to be valid according to ``Clique.validate``.
    """
    n = instance["n"]
    edges = set()
    for u, v in instance["edges"]:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance["k"]

    # Edge cases defined in the problem statement.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Check all subsets of size >= k.
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Verify that every pair is an edge.
            if all(((min(a, b), max(a, b)) in edges) for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the CNF formula is satisfiable.

    The instance is assumed to be valid according to ``Sat.validate``.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Edge case: an empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # No clauses -> trivially satisfiable.
    if not clauses:
        return True

    # Enumerate all assignments.
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
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


def generate_all_graphs(max_n: int):
    """Yield all possible undirected graphs up to ``max_n`` vertices.

    For each ``n`` we iterate over every subset of the possible edges.
    """
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            yield n, edges


def main() -> None:
    total = 0
    passed = 0
    for n, edges in generate_all_graphs(4):  # keep enumeration small for speed
        for k in range(-1, n + 2):  # include some out‑of‑range values
            instance = {"n": n, "edges": edges, "k": k}
            # Validate the source instance – should never raise.
            try:
                Clique.validate(instance)
            except InvalidInstance as exc:
                print(f"Invalid source instance: {instance} – {exc}", file=sys.stderr)
                continue
            total += 1
            expected = clique_bruteforce(instance)
            # Reduce and validate target instance.
            reduced = reduce_instance(instance)
            try:
                Sat.validate(reduced)
            except InvalidInstance as exc:
                print(f"Reduced instance invalid for {instance}: {exc}", file=sys.stderr)
                continue
            actual = sat_bruteforce(reduced)
            if expected == actual:
                passed += 1
            else:
                print("Mismatch!", file=sys.stderr)
                print("Source:", instance, file=sys.stderr)
                print("Expected (Clique):", expected, file=sys.stderr)
                print("Reduced SAT:", reduced, file=sys.stderr)
                print("Actual (Sat):", actual, file=sys.stderr)
    # Write verdict file.
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
