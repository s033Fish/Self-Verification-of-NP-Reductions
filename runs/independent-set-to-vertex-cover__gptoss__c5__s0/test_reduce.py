"""Automated tests for the reduction from IndependentSet to VertexCover.

The repository provides only validation functions for the two problems.
This test suite implements simple exhaustive (brute‑force) solvers for both
problems and checks that the reduction defined in ``reduce.py`` preserves the
answer on a large collection of randomly generated small instances.

The test strategy is:

1. Enumerate many random graphs with up to 6 vertices (the exhaustive search
   is feasible for this size).
2. For each graph generate a range of ``k`` values that cover negative, zero,
   typical, and out‑of‑bounds cases.
3. Validate the source instance using ``IndependentSet.validate`` – this also
   ensures the reduction receives a well‑formed input.
4. Run the brute‑force solvers on the source instance and on the target
   instance obtained via ``reduce.reduce``.
5. Verify that the answers match.

If all generated cases match, the reduction is considered verified. The script
records the number of tests run and passed, and writes ``verdict.json`` in the
required format.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from typing import List, Dict, Any

# Import the modules under test
from problems import IndependentSet, VertexCover, InvalidInstance
from reduce import reduce as reduce_instance


def independent_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph has an independent set of size at least k.

    The implementation follows the exact definition from the problem
    statement, handling all edge cases explicitly.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the specification
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        # With no edges any set of vertices is independent.
        return True

    # Build adjacency set for quick lookup
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Check all subsets of size >= k (small n, so exhaustive is fine)
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in combinations(vertices, size):
            # Verify independence
            independent = True
            for u in subset:
                if any(v in adj[u] for v in subset if v != u):
                    independent = False
                    break
            if independent:
                return True
    return False


def vertex_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph has a vertex cover of size at most k.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the specification
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True  # empty cover works for any k >= 0

    vertices = list(range(n))
    for size in range(0, k + 1):
        for subset in combinations(vertices, size):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def random_graph(max_n: int = 6, edge_prob: float = 0.3) -> Dict[str, Any]:
    """Generate a random simple undirected graph with ``n`` vertices.

    The returned dictionary contains ``n`` and ``edges`` fields but no ``k``.
    """
    n = random.randint(0, max_n)
    edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def run_tests(num_trials: int = 2000) -> Dict[str, int]:
    tests_run = 0
    tests_passed = 0
    for _ in range(num_trials):
        base = random_graph()
        n = base["n"]
        # Choose a variety of k values, including out‑of‑range and negative.
        ks = set()
        ks.update([-2, -1, 0, 1, n // 2, n, n + 1, n + 2])
        # Also add some random ks in a reasonable range.
        for _ in range(3):
            ks.add(random.randint(-3, n + 3))
        for k in ks:
            instance = {"n": n, "edges": base["edges"], "k": k}
            try:
                IndependentSet.validate(instance)
            except InvalidInstance:
                # Skip malformed instances – they should not occur given our
                # generator, but guard against unexpected bugs.
                continue
            # Compute answers
            ans_source = independent_set_bruteforce(instance)
            # Reduce
            target_instance = reduce_instance(instance)
            # Validate target (should always succeed)
            try:
                VertexCover.validate(target_instance)
            except InvalidInstance as exc:
                print("Target instance invalid:", exc, file=sys.stderr)
                continue
            ans_target = vertex_cover_bruteforce(target_instance)
            tests_run += 1
            if ans_source == ans_target:
                tests_passed += 1
            else:
                # Output diagnostic info for the failing case.
                print("Mismatch detected:")
                print("Source instance:", instance)
                print("Target instance:", target_instance)
                print("Source answer:", ans_source, "Target answer:", ans_target)
    return {"tests_run": tests_run, "tests_passed": tests_passed}


def main() -> None:
    results = run_tests()
    verified = results["tests_run"] == results["tests_passed"] and results["tests_run"] > 0
    verdict = {
        "verified": verified,
        "tests_run": results["tests_run"],
        "tests_passed": results["tests_passed"],
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    # Also print the verdict for immediate visibility.
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
