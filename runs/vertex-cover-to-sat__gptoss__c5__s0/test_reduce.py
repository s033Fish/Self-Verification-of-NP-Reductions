"""Automated tests for the vertex-cover-to-sat reduction.

The repository provides a ``reduce`` function that converts a VertexCover
instance into a SAT instance.  The purpose of this script is to verify that
the reduction is *correct*: for every small source instance the answer to
the SAT formula must match the answer to the original Vertex Cover problem.

We implement straightforward brute‑force solvers for both problems based on
the formal definitions in ``problems.py``.  Then we enumerate all graphs up
to a modest size (n ≤ 4) and a range of ``k`` values, run the reduction and
compare the results.

The script prints a JSON object compatible with the required ``verdict``
format: ``{"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}``
which is written to ``verdict.json``.
"""

from __future__ import annotations

import itertools
import json
from typing import List, Dict, Any

from problems import VertexCover, Sat
from reduce import reduce as vc_to_sat


def vertex_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the vertex‑cover instance is a YES instance.

    The instance follows the format defined in ``problems.VertexCover``:
    ``{"n": int, "edges": [[u, v], ...], "k": int}``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True  # empty graph is always covered

    vertices = list(range(n))
    # Enumerate all subsets (2^n) and check size constraint
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Instance format: ``{"num_vars": m, "clauses": [[lit, ...], ...]}`` where
    literals are signed integers.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # A formula with no clauses is trivially satisfiable.
    if not clauses:
        return True
    # Any empty clause makes the formula unsatisfiable.
    if any(len(c) == 0 for c in clauses):
        return False

    # Enumerate all possible assignments (0 = false, 1 = true)
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # index 0 -> var 1
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


def generate_all_graphs(n: int) -> List[List[List[int]]]:
    """Return a list of edge lists representing every undirected simple graph
    on ``n`` vertices.
    """
    vertices = list(range(n))
    possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
    graphs: List[List[List[int]]] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for idx, (u, v) in enumerate(possible_edges):
            if mask & (1 << idx):
                edges.append([u, v])
        graphs.append(edges)
    return graphs


def main() -> None:
    max_n = 4  # keep enumeration tractable
    total_tests = 0
    passed = 0
    for n in range(0, max_n + 1):
        all_graphs = generate_all_graphs(n)
        for edges in all_graphs:
            for k in range(-1, n + 2):  # include values below 0 and above n
                instance: Dict[str, Any] = {"n": n, "edges": edges, "k": k}
                # Validate using the problem class (will raise if malformed)
                VertexCover.validate(instance)
                src_ans = vertex_cover_bruteforce(instance)
                sat_instance = vc_to_sat(instance)
                # Validate the produced SAT instance as well
                Sat.validate(sat_instance)
                tgt_ans = sat_bruteforce(sat_instance)
                total_tests += 1
                if src_ans == tgt_ans:
                    passed += 1
                else:
                    # Print the first failing case for debugging
                    print("Mismatch found:")
                    print(json.dumps({"instance": instance, "sat_instance": sat_instance, "src_ans": src_ans, "tgt_ans": tgt_ans}, indent=2))
    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
