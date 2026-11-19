"""Test suite for the reduction from VertexCover to Clique.

The script enumerates all graphs on up to ``MAX_N`` vertices (inclusive) and
checks that ``reduce`` produces a Clique instance whose answer matches the
answer of the original VertexCover instance.

It implements straightforward brute‑force solvers for both problems based on
the definitions in ``problems.py``.

The script prints a JSON object with the fields required for the final
``verdict.json`` file:

    {
        "verified": <bool>,
        "tests_run": <int>,
        "tests_passed": <int>
    }

The values are also written to ``verdict.json`` for the evaluation harness.
"""

from __future__ import annotations

import json
import itertools
import sys
from pathlib import Path

from problems import VertexCover, Clique
from reduce import reduce as reduce_instance

MAX_N = 5  # keep enumeration tractable (2^(n choose 2) graphs)


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the VertexCover instance is a yes‑instance.

    The implementation follows the exact specification in the docstring of
    ``VertexCover``.  It enumerates all subsets of vertices up to size ``k`` and
    checks whether each edge has at least one endpoint in the subset.
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
        return True  # empty edge set is covered by the empty set

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


def clique_bruteforce(instance: dict) -> bool:
    """Return True iff the Clique instance is a yes‑instance.

    The implementation follows the exact specification in the docstring of
    ``Clique``.  It checks all subsets of vertices of size ``k`` (or larger) for
    being a clique.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    vertices = list(range(n))
    # Need at least k vertices; we can stop early when we find any clique of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Check if every pair is an edge
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def enumerate_graphs(n: int):
    """Yield all simple undirected graphs on ``n`` vertices.

    Each graph is represented as a list of edges ``[u, v]`` with ``u < v``.
    """
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = []
        for i, (u, v) in enumerate(pairs):
            if mask & (1 << i):
                edges.append([u, v])
        yield edges


def main() -> None:
    total_tests = 0
    passed = 0

    for n in range(0, MAX_N + 1):
        for edges in enumerate_graphs(n):
            # Test a range of k values covering edge cases
            ks = list(range(-1, n + 2))  # -1, 0, ..., n, n+1
            for k in ks:
                vc_instance = {"n": n, "edges": edges, "k": k}
                # Validate instance – should not raise
                VertexCover.validate(vc_instance)
                # Compute answers
                vc_ans = vertex_cover_bruteforce(vc_instance)
                # Reduce
                try:
                    clique_instance = reduce_instance(vc_instance)
                except Exception as e:
                    print(f"Reduction raised on instance {vc_instance}: {e}", file=sys.stderr)
                    continue
                # Validate reduced instance – should not raise
                Clique.validate(clique_instance)
                clique_ans = clique_bruteforce(clique_instance)
                total_tests += 1
                if vc_ans == clique_ans:
                    passed += 1
                else:
                    print(
                        f"Mismatch for n={n}, edges={edges}, k={k}: vc={vc_ans}, clique={clique_ans}",
                        file=sys.stderr,
                    )

    verdict = {
        "verified": passed == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed,
    }
    # Write verdict.json
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
