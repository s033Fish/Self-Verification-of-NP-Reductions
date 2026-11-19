"""Automated tests for the VertexCover → SAT reduction.

The script enumerates small graph instances, runs the provided ``reduce``
function, validates the produced SAT instance and checks that the answer of
the SAT instance matches the answer of the original Vertex Cover instance.

Both problems are solved by exhaustive search because the instances are tiny
(`n` ≤ 5).  The script records how many tests were executed and how many
passed, then writes a ``verdict.json`` file as required by the task.
"""

from __future__ import annotations

import json
import itertools
import sys
from typing import List, Dict, Any

# Import the problem definitions and the reduction implementation.
from problems import VertexCover, Sat, InvalidInstance
from reduce import reduce as reduce_instance


def solve_vertex_cover(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for Vertex Cover.

    Returns ``True`` iff the graph has a vertex cover of size at most ``k``.
    """
    n = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k = instance["k"]

    # Edge cases from the specification.
    if k < 0:
        return False
    if not edges:
        return True  # empty graph is always covered
    if k >= n:
        return True

    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            chosen = set(subset)
            for u, v in edges:
                if u not in chosen and v not in chosen:
                    covered = False
                    break
            if covered:
                return True
    return False


def solve_sat(instance: Dict[str, Any]) -> bool:
    """Brute‑force SAT solver.

    Returns ``True`` iff the CNF formula is satisfiable.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Empty clause makes the formula unsatisfiable.
    for clause in clauses:
        if not clause:
            return False

    # No clauses => trivially satisfiable.
    if not clauses:
        return True

    for assignment in itertools.product([False, True], repeat=m):
        # assignment[i] corresponds to variable i+1
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


def generate_all_instances(max_n: int = 5) -> List[Dict[str, Any]]:
    """Generate a representative set of VertexCover instances.

    For each ``n`` we consider all possible edge subsets (up to a limit to
    keep runtime reasonable) and a range of ``k`` values.
    """
    instances: List[Dict[str, Any]] = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = list(itertools.combinations(vertices, 2))
        # Limit the number of edge subsets for larger n to keep the test fast.
        edge_subsets = list(itertools.chain.from_iterable(
            itertools.combinations(possible_edges, r) for r in range(min(len(possible_edges), 4) + 1)
        ))
        for edges in edge_subsets:
            edges_list = [list(e) for e in edges]
            for k in range(-1, n + 2):  # include values below 0 and above n
                instances.append({"n": n, "edges": edges_list, "k": k})
    return instances


def main() -> None:
    tests_run = 0
    tests_passed = 0
    for vc_instance in generate_all_instances():
        # Validate the source instance (should never raise).
        try:
            VertexCover.validate(vc_instance)
        except InvalidInstance as exc:
            print("Invalid source instance generated:", exc, file=sys.stderr)
            continue

        # Compute expected answers.
        expected_vc = solve_vertex_cover(vc_instance)
        # Reduce and validate target.
        try:
            sat_instance = reduce_instance(vc_instance)
            Sat.validate(sat_instance)
        except InvalidInstance as exc:
            print("Reduction produced invalid SAT instance:", exc, file=sys.stderr)
            continue

        expected_sat = solve_sat(sat_instance)
        tests_run += 1
        if expected_vc == expected_sat:
            tests_passed += 1
        else:
            print("Mismatch!", vc_instance, "expected", expected_vc, "got", expected_sat, file=sys.stderr)

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

