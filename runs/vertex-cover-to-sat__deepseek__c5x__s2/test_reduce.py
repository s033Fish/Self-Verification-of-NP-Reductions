"""Automated tests for the VertexCover → SAT reduction.

The repository provides only validation functions for the two problems.
To verify the correctness of ``reduce.py`` we implement brute‑force
solvers for both problems and compare the answer of the original instance
with the answer of the reduced SAT instance.

The tests enumerate a large number of small random instances (n ≤ 3) so
that the SAT instance stays tiny even after adding the auxiliary variables
used by the Sinz sequential counter. For each generated instance we:

1. Validate the source instance using ``VertexCover.validate``.
2. Compute the correct answer with ``brute_vertex_cover``.
3. Reduce the instance via ``reduce``.
4. Validate the target instance using ``Sat.validate``.
5. Compute the correct answer with ``brute_sat``.
6. Check that both answers coincide.

The script records the number of tests executed and the number that passed.
It finally writes ``verdict.json`` as required by the task description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product
from pathlib import Path

# Import the problem definitions and the reduction implementation.
from problems import VertexCover, Sat
from reduce import reduce as reduce_instance


def brute_vertex_cover(instance: dict) -> bool:
    """Return True iff the graph has a vertex cover of size at most k.

    The instance follows the format defined in ``VertexCover``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # Enumerate all subsets of vertices up to size k.
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in combinations(vertices, r):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


def brute_sat(instance: dict) -> bool:
    """Return True iff the CNF formula is satisfiable.

    ``instance`` follows the format defined in ``Sat``.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False
    # Enumerate all assignments of m boolean variables.
    for bits in product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def generate_random_instance(max_n: int = 3) -> dict:
    """Generate a random VertexCover instance with n ≤ max_n.

    The graph is simple (no parallel edges, no self‑loops) as required by
    the validation function.
    """
    n = random.randint(0, max_n)
    # All possible unordered edges.
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for e in possible_edges:
        if random.choice([True, False]):
            edges.append(list(e))
    k = random.randint(-1, n + 1)  # allow some out‑of‑range values
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    # Run a fixed number of random tests.
    for _ in range(200):
        src = generate_random_instance()
        # Validate source instance – this will raise if malformed.
        VertexCover.validate(src)
        src_answer = brute_vertex_cover(src)
        tgt = reduce_instance(src)
        # Validate target instance.
        Sat.validate(tgt)
        tgt_answer = brute_sat(tgt)
        tests_run += 1
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            # Print details for debugging.
            print("Mismatch!", file=sys.stderr)
            print("source", src, file=sys.stderr)
            print("src_answer", src_answer, file=sys.stderr)
            print("target", tgt, file=sys.stderr)
            print("tgt_answer", tgt_answer, file=sys.stderr)
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    if verdict["verified"]:
        print("All tests passed")
    else:
        print("Some tests failed", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

