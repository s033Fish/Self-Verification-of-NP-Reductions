"""Automated tests for the IndependentSet → Clique reduction.

The repository provides a ``reduce`` function that converts an instance of the
source problem (Independent Set) into an instance of the target problem (Clique).
This test suite verifies that the reduction is correct by comparing the answer
of a brute‑force solver on the original instance with the answer of a brute‑
force solver on the reduced instance.

The tests enumerate *all* graphs up to a modest size (n ≤ 5) and a range of
values for ``k``.  For each combination we check that:

* ``reduce`` returns a well‑formed Clique instance (validation is performed by
  the reduction itself).
* The Independent Set solver returns ``True`` iff the Clique solver returns
  ``True`` on the reduced instance.

The results are written to ``verdict.json`` as required by the task.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Any

# Import the reduction and validation classes from the repository
from reduce import reduce as reduce_instance
from problems import IndependentSet, Clique


def _edge_set(edges: List[List[int]]) -> set[frozenset[int]]:
    """Utility to convert a list of edge pairs to a set of unordered frozensets."""
    return {frozenset((u, v)) for u, v in edges}


def independent_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph has an independent set of size at least ``k``.

    The implementation enumerates all subsets of vertices using bit masks –
    sufficient for the tiny graphs used in the exhaustive tests.
    """
    n = instance["n"]
    edges = _edge_set(instance["edges"])
    k = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k > n:
        return False

    # Enumerate subsets
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            # Check if subset is independent
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    independent = False
                    break
            if independent:
                return True
    return False


def clique_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph has a clique of size at least ``k``.

    Mirrors the independent‑set solver but checks for the presence of all
    required edges between vertices.
    """
    n = instance["n"]
    edges = _edge_set(instance["edges"])
    k = instance["k"]

    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            # Verify every pair is an edge
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def main() -> None:
    total_tests = 0
    passed_tests = 0
    # Enumerate graph sizes up to 5 (larger would explode combinatorially)
    for n in range(0, 6):
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        # Iterate over all subsets of the possible edge list
        for edge_mask in range(1 << len(possible_edges)):
            edges: List[List[int]] = []
            for i, (u, v) in enumerate(possible_edges):
                if (edge_mask >> i) & 1:
                    edges.append([u, v])
            # Test a range of k values, including edge cases
            for k in range(-1, n + 2):
                total_tests += 1
                instance: Dict[str, Any] = {"n": n, "edges": edges, "k": k}
                # Validate source instance (should always succeed)
                IndependentSet.validate(instance)
                # Compute expected answers
                expected = independent_set_bruteforce(instance)
                # Reduce and solve target
                reduced = reduce_instance(instance)
                # The reduction already validates the target instance
                got = clique_bruteforce(reduced)
                if expected == got:
                    passed_tests += 1
                else:
                    # Print a diagnostic for the first failure and abort
                    print("Mismatch found!", file=sys.stderr)
                    print(f"Original instance: {instance}", file=sys.stderr)
                    print(f"Reduced instance: {reduced}", file=sys.stderr)
                    print(f"Expected (IndependentSet): {expected}", file=sys.stderr)
                    print(f"Got (Clique): {got}", file=sys.stderr)
                    # Write verdict with failure
                    verdict = {
                        "verified": False,
                        "tests_run": total_tests,
                        "tests_passed": passed_tests,
                    }
                    with open("verdict.json", "w", encoding="utf-8") as f:
                        json.dump(verdict, f)
                    sys.exit(1)

    # All tests passed
    verdict = {
        "verified": True,
        "tests_run": total_tests,
        "tests_passed": passed_tests,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()

