"""Automated tests for the reduction from VertexCover to SetCover.

The repository only provides the problem definitions and the reduction.
This test suite implements brute‑force solvers for both problems and
exhaustively checks small instances to verify that the reduction preserves
the answer (YES/NO) exactly.

The script is executed as part of the verification step. It writes a
``verdict.json`` file describing the outcome.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

# Import the problem definitions and the reduction implementation.
from problems import VertexCover, SetCover
from reduce import reduce as reduce_instance


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the VertexCover instance has a cover of size at most k.

    The implementation enumerates all subsets of vertices up to k and checks
    whether each edge is incident to at least one chosen vertex.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases defined in the problem statement.
    if k < 0:
        return False
    if not edges:
        return True  # empty graph is always covered
    if k >= n:
        return True

    vertices = list(range(n))
    # Enumerate subsets of size up to k.
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def set_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the SetCover instance can be covered with at most k sets.
    """
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]

    if k < 0:
        return False
    if u == 0:
        return True
    # quick impossibility check: if some element never appears.
    all_elements = set()
    for s in sets:
        all_elements.update(s)
    if any(elem not in all_elements for elem in range(u)):
        return False
    if k >= len(sets):
        # using all sets trivially covers everything (if possible)
        return all_elements == set(range(u))

    indices = list(range(len(sets)))
    for r in range(k + 1):
        for combo in itertools.combinations(indices, r):
            covered = set()
            for idx in combo:
                covered.update(sets[idx])
            if covered == set(range(u)):
                return True
    return False


def generate_vertex_cover_instances(max_n: int = 4) -> list[dict]:
    """Generate all valid VertexCover instances for n up to ``max_n``.

    For each n we consider every possible subset of the ``n choose 2`` edges
    and a range of k values covering edge cases.
    """
    instances: list[dict] = []
    for n in range(max_n + 1):
        # All possible edges (undirected, u < v)
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for edge_subset in itertools.product([0, 1], repeat=len(possible_edges)):
            edges = [list(possible_edges[i]) for i, bit in enumerate(edge_subset) if bit]
            # Choose k values covering negative, zero, typical, and >= n
            ks = list(range(-1, n + 2))  # -1, 0, ..., n, n+1
            for k in ks:
                instance = {"n": n, "edges": edges, "k": k}
                # Validation should succeed for all generated instances.
                VertexCover.validate(instance)
                instances.append(instance)
    return instances


def main() -> None:
    instances = generate_vertex_cover_instances(max_n=4)
    total = len(instances)
    passed = 0
    mismatches = []

    for instance in instances:
        vc_answer = vertex_cover_bruteforce(instance)
        reduced = reduce_instance(instance)
        sc_answer = set_cover_bruteforce(reduced)
        if vc_answer == sc_answer:
            passed += 1
        else:
            mismatches.append({"instance": instance, "reduced": reduced, "vc": vc_answer, "sc": sc_answer})

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    # Write verdict file
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))

    if not verdict["verified"]:
        print("Reduction failed on some instances.")
        for m in mismatches[:5]:  # show a few examples
            print(json.dumps(m, indent=2))
        sys.exit(1)
    else:
        print(f"All {total} tests passed.")


if __name__ == "__main__":
    main()
