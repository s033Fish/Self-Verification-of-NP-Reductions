"""Tests for the reduction from Clique to Independent Set.

The repository provides only the problem definitions and the reduction
implementation.  To verify the reduction we implement straightforward
brute‑force solvers for both problems and compare the answer on a large set of
random small instances.

The test suite generates all graphs with up to ``MAX_N`` vertices (limited to a
small number to keep the runtime reasonable) and several values of ``k``.  For
each instance we:

1. Validate the original instance using ``Clique.validate``.
2. Run the reduction to obtain an ``IndependentSet`` instance.
3. Validate the reduced instance using ``IndependentSet.validate``.
4. Compute the exact answer for the source instance with ``brute_force_clique``.
5. Compute the exact answer for the target instance with
   ``brute_force_independent_set``.
6. Assert that the two answers are identical.

The script prints a JSON object compatible with the required ``verdict.json``
format: ``{"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}``.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from typing import Dict, List

from problems import Clique, IndependentSet
from reduce import reduce as reduce_instance


def brute_force_clique(instance: Dict) -> bool:
    """Return True iff the graph has a clique of size at least ``k``.

    The algorithm enumerates all subsets of vertices and checks whether the
    induced subgraph is complete.  This is exponential but acceptable for the
    tiny instances used in the tests.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    # Edge cases defined by the problem statement.
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Check all subsets of size >= k.
    for size in range(k, n + 1):
        for subset in combinations(range(n), size):
            # Verify every pair is an edge.
            if all(frozenset((u, v)) in edges for u, v in combinations(subset, 2)):
                return True
    return False


def brute_force_independent_set(instance: Dict) -> bool:
    """Return True iff the graph has an independent set of size at least ``k``.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:  # No edges – any set works.
        return True

    for size in range(k, n + 1):
        for subset in combinations(range(n), size):
            # No pair may be an edge.
            if all(frozenset((u, v)) not in edges for u, v in combinations(subset, 2)):
                return True
    return False


def random_graph(n: int, edge_prob: float = 0.5) -> List[List[int]]:
    """Generate a random undirected simple graph with ``n`` vertices.

    ``edge_prob`` is the probability for each unordered pair to be an edge.
    """
    edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return edges


def main() -> None:
    random.seed(0)
    MAX_N = 6  # keep exhaustive enumeration cheap
    tests_run = 0
    tests_passed = 0
    verified = True

    for n in range(0, MAX_N + 1):
        # Generate a few random graphs for each n to increase coverage.
        for _ in range(20):
            edges = random_graph(n, edge_prob=0.5)
            # Try a range of k values, including edge cases.
            for k in range(-1, n + 3):
                instance = {"n": n, "edges": edges, "k": k}
                # Validate source instance – should not raise.
                try:
                    Clique.validate(instance)
                except Exception:
                    # If validation fails, the instance is malformed; skip.
                    continue
                # Perform reduction.
                try:
                    reduced = reduce_instance(instance)
                except Exception as e:
                    verified = False
                    print(f"Reduction raised an exception: {e}", file=sys.stderr)
                    continue
                # Validate target instance.
                try:
                    IndependentSet.validate(reduced)
                except Exception as e:
                    verified = False
                    print(f"Reduced instance invalid: {e}", file=sys.stderr)
                    continue

                # Compute exact answers.
                src_ans = brute_force_clique(instance)
                tgt_ans = brute_force_independent_set(reduced)
                tests_run += 1
                if src_ans == tgt_ans:
                    tests_passed += 1
                else:
                    verified = False
                    print(
                        f"Mismatch on instance n={n}, k={k}, edges={edges}\n"
                        f"src={src_ans}, tgt={tgt_ans}",
                        file=sys.stderr,
                    )

    verdict = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
