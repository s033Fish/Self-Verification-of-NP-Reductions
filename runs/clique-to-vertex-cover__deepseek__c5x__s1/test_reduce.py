"""Test the reduction from Clique to VertexCover.

The script brute‑forces the answer to both problems for all small graphs
and compares the answer of the reduction with the direct answers.

If every test passes we consider the reduction verified.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

# Import the reduction function
from reduce import reduce as reduce_instance


def is_clique(instance: dict) -> bool:
    """Return True iff the Clique instance is a YES instance.

    Brute‑force check all subsets of vertices of size >= k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    # Edge cases from the definition
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    edge_set = {frozenset(e) for e in edges}
    vertices = list(range(n))
    # Check subsets of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # every pair must be an edge
            if all(frozenset(pair) in edge_set for pair in itertools.combinations(subset, 2)):
                return True
    return False


def is_vertex_cover(instance: dict) -> bool:
    """Return True iff the VertexCover instance is a YES instance.

    Brute‑force check all subsets of vertices of size <= k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    # Edge cases
    if k < 0:
        return False
    if not edges:
        return True  # empty edge set always covered
    if k >= n:
        return True

    edge_set = [frozenset(e) for e in edges]
    vertices = list(range(n))
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(vertices, size):
            covered = all(any(v in edge for v in subset) for edge in edge_set)
            if covered:
                return True
    return False


def generate_all_graphs(n: int):
    """Yield all undirected simple graphs on n vertices.

    Each graph is represented as a list of edges [u, v] with u < v.
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
    # Test for n up to 5 (manageable)
    for n in range(0, 6):
        for edges in generate_all_graphs(n):
            for k in range(-1, n + 3):  # include some out‑of‑range values
                clique_inst = {"n": n, "edges": edges, "k": k}
                expected_clique = is_clique(clique_inst)
                reduced = reduce_instance(clique_inst)
                expected_vc = is_vertex_cover(reduced)
                total += 1
                if expected_clique == expected_vc:
                    passed += 1
                else:
                    print("Mismatch found:")
                    print(json.dumps({"clique": clique_inst, "reduced": reduced}, indent=2))
                    print(f"expected_clique={expected_clique}, expected_vc={expected_vc}")
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
