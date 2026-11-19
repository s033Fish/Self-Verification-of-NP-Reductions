"""Automated tests for the reduction from Clique to VertexCover.

The repository provides only validation functions for the two problems.
This test suite implements straightforward brute‑force solvers for both
decision problems and checks that the reduction defined in ``reduce.py``
preserves the answer on a large collection of small instances.

The script enumerates all graphs on up to 5 vertices (which is feasible –
2^(5 choose 2) = 1024 graphs) and a range of ``k`` values covering the
edge cases described in the problem statements. For each instance we:

1. Validate the original Clique instance using ``Clique.validate``.
2. Compute the correct answer with ``solve_clique``.
3. Apply ``reduce`` to obtain a VertexCover instance and validate it.
4. Compute the correct answer with ``solve_vertex_cover``.
5. Verify that the answers are equal.

If all tests pass, ``verified`` is true; otherwise false. The script writes
the result to ``verdict.json`` as required by the task description.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

# Import problem definitions and the reduction implementation.
from problems import Clique, VertexCover
from reduce import reduce as reduce_instance


def solve_clique(instance: dict) -> bool:
    """Brute‑force decision solver for Clique.

    Returns True iff the graph has a clique of size at least ``k``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge‑case handling as per the problem statement.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Build adjacency set for O(1) edge queries.
    adj = {frozenset((u, v)) for u, v in edges}

    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            if all(frozenset((a, b)) in adj for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def solve_vertex_cover(instance: dict) -> bool:
    """Brute‑force decision solver for VertexCover.

    Returns True iff the graph has a vertex cover of size at most ``k``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True

    vertices = list(range(n))
    for size in range(k + 1):
        for subset in itertools.combinations(vertices, size):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


def generate_all_graphs(n: int) -> List[List[Tuple[int, int]]]:
    """Return a list of edge lists representing every undirected graph on ``n`` vertices.
    Each edge is a tuple (u, v) with u < v.
    """
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    all_graphs: List[List[Tuple[int, int]]] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[Tuple[int, int]] = []
        for i, e in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append(e)
        all_graphs.append(edges)
    return all_graphs


def main() -> None:
    total_tests = 0
    passed_tests = 0
    verified = True

    max_n = 5  # keep runtime reasonable
    for n in range(max_n + 1):
        all_graphs = generate_all_graphs(n)
        ks = list(range(-2, n + 3))
        for edges in all_graphs:
            edge_list = [[u, v] for u, v in edges]
            for k in ks:
                source_instance = {"n": n, "edges": edge_list, "k": k}
                try:
                    Clique.validate(source_instance)
                except Exception as e:
                    print(f"Invalid source instance {source_instance}: {e}", file=sys.stderr)
                    verified = False
                    continue
                expected = solve_clique(source_instance)
                target_instance = reduce_instance(source_instance)
                try:
                    VertexCover.validate(target_instance)
                except Exception as e:
                    print(f"Invalid target instance {target_instance}: {e}", file=sys.stderr)
                    verified = False
                    continue
                actual = solve_vertex_cover(target_instance)
                total_tests += 1
                if expected == actual:
                    passed_tests += 1
                else:
                    verified = False
                    print(
                        "Mismatch found:\n",
                        f"source={source_instance}\n",
                        f"target={target_instance}\n",
                        f"expected={expected}, actual={actual}\n",
                        file=sys.stderr,
                    )
    verdict = {
        "verified": verified,
        "tests_run": total_tests,
        "tests_passed": passed_tests,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
