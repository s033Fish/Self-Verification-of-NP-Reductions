"""Automated tests for the Clique → VertexCover reduction.

The repository provides only validation functions for the two problems and a
reduction implementation (``reduce.py``).  This test suite implements brute‑force
solvers for both problems, enumerates a large set of small instances, and checks
that the reduction preserves the answer.

If **all** generated instances satisfy the equivalence, ``verdict.json`` will be
written with ``{"verified": true, ...}``.  Otherwise ``verified`` will be false
and the failing instance will be printed for debugging.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import Clique, VertexCover
from reduce import reduce as reduce_instance


def solve_clique(instance: dict) -> bool:
    """Brute‑force solver for the Clique problem.

    Returns ``True`` iff the graph has a clique of size at least ``k``.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]

    # Edge‑case handling as described in the docstring.
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
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def solve_vertex_cover(instance: dict) -> bool:
    """Brute‑force solver for the Vertex Cover problem.

    Returns ``True`` iff there exists a vertex cover of size at most ``k``.
    """
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]

    if k < 0:
        return False
    if not edges:
        return True  # empty set covers empty edge set
    if k >= n:
        return True

    vertices = list(range(n))
    for size in range(k + 1):
        for subset in itertools.combinations(vertices, size):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def generate_all_instances(max_n: int = 5) -> list[dict]:
    """Generate a comprehensive list of small Clique instances.

    For each ``n`` we enumerate every possible edge set (the power set of the
    ``n choose 2`` possible edges) and a range of ``k`` values covering the
    relevant edge cases.
    """
    instances = []
    for n in range(max_n + 1):
        # All possible unordered pairs.
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for edge_mask in range(1 << len(possible_edges)):
            edges = [list(possible_edges[i]) for i in range(len(possible_edges)) if (edge_mask >> i) & 1]
            # Choose k values: a few below 0, 0, 1, up to n+1
            ks = list(range(-1, n + 2))
            for k in ks:
                instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    instances = generate_all_instances(max_n=5)
    total = len(instances)
    passed = 0
    for idx, inst in enumerate(instances, 1):
        # Validate source instance (should be valid by construction).
        try:
            Clique.validate(inst)
        except Exception as e:
            print(f"Invalid generated instance #{idx}: {e}", file=sys.stderr)
            continue
        expected = solve_clique(inst)
        # Apply reduction.
        try:
            reduced = reduce_instance(inst)
        except Exception as e:
            print(f"Reduction raised on instance #{idx}: {e}", file=sys.stderr)
            continue
        # Validate reduced instance.
        try:
            VertexCover.validate(reduced)
        except Exception as e:
            print(f"Reduced instance invalid for #{idx}: {e}", file=sys.stderr)
            continue
        actual = solve_vertex_cover(reduced)
        if expected == actual:
            passed += 1
        else:
            print("Mismatch found:")
            print("Original instance:", json.dumps(inst))
            print("Reduced instance:", json.dumps(reduced))
            print("Expected (Clique):", expected)
            print("Actual   (VertexCover):", actual)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

