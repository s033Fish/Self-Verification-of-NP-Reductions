"""Tests for the reduction from VertexCover to DominatingSet.

The test suite generates all graphs on up to ``MAX_N`` vertices (including
isolated vertices) and a range of ``k`` values. For each source instance it
computes the exact answer using a brute‑force solver, applies the reduction
implemented in ``reduce.py`` and checks that the answer for the target
instance (computed with another brute‑force solver) matches.

If all generated instances satisfy the equivalence, the reduction is deemed
correct for the tested domain.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

# Import the reduction function and problem definitions.
from reduce import reduce as reduce_instance  # noqa: N813
from problems import VertexCover, DominatingSet


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the instance has a vertex cover of size at most k.

    The implementation follows the exact definition from the problem
    statement, handling all edge cases.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the specification.
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        # Empty edge set is always covered by the empty set.
        return True

    vertices = list(range(n))
    # Test all subsets up to size k.
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


def dominating_set_bruteforce(instance: dict) -> bool:
    """Return True iff the instance has a dominating set of size at most k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True
    if n == 0:
        return True

    # Build adjacency list including self (a vertex dominates itself).
    adj = [set() for _ in range(n)]
    for i in range(n):
        adj[i].add(i)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            dominated = set()
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def generate_all_graphs(n: int):
    """Yield all undirected simple graphs on ``n`` vertices.

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
    MAX_N = 5  # keep runtime reasonable
    total = 0
    passed = 0
    for n in range(MAX_N + 1):
        for edges in generate_all_graphs(n):
            # Test a range of k values covering edge cases.
            for k in range(-1, n + 2):
                src_instance = {"n": n, "edges": edges, "k": k}
                # Validate using the problem classes (will raise if malformed).
                VertexCover.validate(src_instance)
                # Compute exact answers.
                src_answer = vertex_cover_bruteforce(src_instance)
                # Apply reduction.
                tgt_instance = reduce_instance(src_instance)
                DominatingSet.validate(tgt_instance)
                tgt_answer = dominating_set_bruteforce(tgt_instance)
                total += 1
                if src_answer == tgt_answer:
                    passed += 1
                else:
                    # Print a diagnostic and abort.
                    print("Reduction failed for instance:")
                    print(json.dumps(src_instance, indent=2))
                    print("Reduced to:")
                    print(json.dumps(tgt_instance, indent=2))
                    print(f"src_answer={src_answer}, tgt_answer={tgt_answer}")
                    sys.exit(1)
    # Write verdict file.
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
