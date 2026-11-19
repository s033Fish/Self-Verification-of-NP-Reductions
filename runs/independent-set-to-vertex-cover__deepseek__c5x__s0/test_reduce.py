"""Test the reduction from Independent Set to Vertex Cover.

The script enumerates all small graphs (up to 5 vertices) and a range of k
values, solves both problems by brute force, applies the reduction, and checks
that the answers match.  It also verifies that the reduction output validates
against the VertexCover problem definition.

The script prints a JSON object with the verification result that will be
written to ``verdict.json`` by the surrounding automation.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import problems
from reduce import reduce as reduce_instance


def independent_set_solver(instance: dict) -> bool:
    """Brute‑force solver for Independent Set.

    Returns True iff the graph has an independent set of size at least k.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k > n:
        return False
    # Enumerate all subsets of vertices
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            subset_set = set(subset)
            # check independence
            if all(not (u in subset_set and v in subset_set) for u, v in edges):
                return True
    return False


def vertex_cover_solver(instance: dict) -> bool:
    """Brute‑force solver for Vertex Cover.

    Returns True iff the graph has a vertex cover of size at most k.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    # Edge cases from the problem statement
    if k < 0:
        return False
    if k >= n:
        return True
    # Enumerate all subsets up to size k
    for r in range(0, k + 1):
        for subset in itertools.combinations(range(n), r):
            subset_set = set(subset)
            # check cover
            if all(u in subset_set or v in subset_set for u, v in edges):
                return True
    return False


def generate_all_graphs(n: int):
    """Yield all simple undirected graphs on n vertices.

    Each graph is represented as a list of edges ``[u, v]`` with ``u < v``.
    """
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        yield edges


def main() -> None:
    total = 0
    passed = 0
    # Test graphs up to 5 vertices
    for n in range(0, 6):
        for edges in generate_all_graphs(n):
            for k in range(-2, n + 3):
                instance = {"n": n, "edges": edges, "k": k}
                # Validate source instance
                try:
                    problems.IndependentSet.validate(instance)
                except Exception as exc:
                    print(f"Invalid source instance {instance}: {exc}", file=sys.stderr)
                    continue
                total += 1
                indep_ans = independent_set_solver(instance)
                # Apply reduction
                reduced = reduce_instance(instance)
                # Validate reduced instance
                try:
                    problems.VertexCover.validate(reduced)
                except Exception as exc:
                    # Reduction produced invalid instance → fail
                    print(f"Reduction produced invalid target instance {reduced}: {exc}", file=sys.stderr)
                    continue
                vc_ans = vertex_cover_solver(reduced)
                if indep_ans == vc_ans:
                    passed += 1
                else:
                    print(
                        f"Mismatch for n={n}, edges={edges}, k={k}: independent={indep_ans}, vertex_cover={vc_ans}",
                        file=sys.stderr,
                    )
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    # Write verdict.json in the current directory
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
