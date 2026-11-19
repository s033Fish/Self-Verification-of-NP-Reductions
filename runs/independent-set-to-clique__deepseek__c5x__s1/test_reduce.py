"""Test the reduction from Independent Set to Clique.

The repository provides a ``reduce`` function that maps an instance of the
``IndependentSet`` problem to an instance of the ``Clique`` problem.  To verify
that this reduction is correct we implement exhaustive (brute‑force) solvers
for both problems and compare the answers on a large set of small random
instances.

The script performs the following steps:

1. Enumerate all graphs with up to ``MAX_N`` vertices (``MAX_N = 5``).  For each
   ``n`` we iterate over every possible subset of the ``n*(n-1)/2`` potential
   edges.  This yields a manageable number of instances (2^{10}=1024 for
   ``n=5``).
2. For each graph we test a range of ``k`` values (``k`` from ``-2`` to
   ``n+2``) to cover the edge‑case handling described in the problem
   definitions.
3. For each source instance we:
   * Validate the instance using ``IndependentSet.validate``.
   * Compute the correct answer with ``solve_independent_set``.
   * Reduce the instance with ``reduce`` and validate the target instance
     using ``Clique.validate``.
   * Compute the answer for the reduced instance with ``solve_clique``.
   * Verify that both answers are identical.

The script records the total number of tests executed and how many passed.
It writes a ``verdict.json`` file in the repository root with the required
structure.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import problems  # The module containing IndependentSet and Clique definitions
from reduce import reduce


def solve_independent_set(instance: dict) -> bool:
    """Brute‑force solver for Independent Set.

    Returns ``True`` iff the graph contains an independent set of size at least
    ``k``.  Implements the exact semantics from the docstring of
    ``IndependentSet``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge‑case handling
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        # No edges – any set of vertices is independent
        return True

    # Build adjacency set for fast lookup
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Enumerate subsets of vertices of size >= k (small n, brute force ok)
    vertices = list(range(n))
    for r in range(k, n + 1):
        for subset in itertools.combinations(vertices, r):
            # Check if subset is independent
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if v in adj[u]:
                    independent = False
                    break
            if independent:
                return True
    return False


def solve_clique(instance: dict) -> bool:
    """Brute‑force solver for Clique.

    Returns ``True`` iff the graph contains a clique of size at least ``k``.
    Mirrors the semantics from the ``Clique`` docstring.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Build adjacency set
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    vertices = list(range(n))
    for r in range(k, n + 1):
        for subset in itertools.combinations(vertices, r):
            # Every pair must be adjacent
            clique = True
            for u, v in itertools.combinations(subset, 2):
                if v not in adj[u]:
                    clique = False
                    break
            if clique:
                return True
    return False


def generate_all_graphs(n: int):
    """Yield all undirected simple graphs on ``n`` vertices.

    Each graph is represented as a list of edges ``[u, v]`` with ``u < v``.
    """
    potential_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(potential_edges)):
        edges = []
        for i, (u, v) in enumerate(potential_edges):
            if mask & (1 << i):
                edges.append([u, v])
        yield edges


def main() -> None:
    MAX_N = 5
    total_tests = 0
    passed_tests = 0

    for n in range(MAX_N + 1):
        for edges in generate_all_graphs(n):
            for k in range(-2, n + 3):
                source_instance = {"n": n, "edges": edges, "k": k}
                # Validate source instance (should not raise)
                try:
                    problems.IndependentSet.validate(source_instance)
                except Exception as exc:
                    print(f"Invalid source instance {source_instance}: {exc}", file=sys.stderr)
                    continue

                source_answer = solve_independent_set(source_instance)
                reduced = reduce(source_instance)
                # Validate reduced instance as Clique
                try:
                    problems.Clique.validate(reduced)
                except Exception as exc:
                    print(f"Invalid reduced instance {reduced}: {exc}", file=sys.stderr)
                    continue
                target_answer = solve_clique(reduced)
                total_tests += 1
                if source_answer == target_answer:
                    passed_tests += 1
                else:
                    print(
                        "Mismatch!", source_instance, "=>", reduced,
                        f"source={source_answer} target={target_answer}",
                        file=sys.stderr,
                    )

    verdict = {
        "verified": total_tests == passed_tests,
        "tests_run": total_tests,
        "tests_passed": passed_tests,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

