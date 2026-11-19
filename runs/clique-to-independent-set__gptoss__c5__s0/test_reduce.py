"""Test suite for the reduction from Clique to IndependentSet.

The repository provides only validation code and the reduction implementation.
This file defines brute‑force solvers for the source (Clique) and target
IndependentSet problems, enumerates a variety of small graph instances, runs the
reduction on each, and checks that the answers agree.

The script produces a ``verdict.json`` file with the fields required by the
task description:

    {
        "verified": <bool>,
        "tests_run": <int>,
        "tests_passed": <int>
    }

If any test fails ``verified`` is ``false``.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Any

from problems import Clique, IndependentSet
from reduce import reduce as reduction


def solve_clique(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for the Clique problem.

    Returns ``True`` iff the graph contains a clique of size at least ``k``.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    # Check all subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Verify every pair is an edge
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def solve_independent_set(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for the Independent Set problem.

    Returns ``True`` iff the graph contains an independent set of size at least
    ``k``.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:  # no edges -> any set works
        return True

    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # No pair should be an edge
            if all(frozenset((u, v)) not in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def generate_all_instances(max_n: int = 5) -> List[Dict[str, Any]]:
    """Generate a list of all graph instances up to ``max_n`` vertices.

    For each graph we also generate a range of ``k`` values covering the edge
    cases: ``-1, 0, 1, n, n+1``.
    """
    instances: List[Dict[str, Any]] = []
    for n in range(0, max_n + 1):
        # All possible undirected edges without self‑loops
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for edge_mask in range(1 << len(possible_edges)):
            edges: List[List[int]] = []
            for i, (u, v) in enumerate(possible_edges):
                if edge_mask & (1 << i):
                    edges.append([u, v])
            # Choose a set of k values to test; include a few beyond the range
            ks = set([-1, 0, 1, n, n + 1])
            # Also test a couple of intermediate values when n >= 2
            if n >= 2:
                ks.add(2)
                ks.add(n - 1)
            for k in ks:
                instance = {"n": n, "edges": edges, "k": k}
                instances.append(instance)
    return instances


def main() -> None:
    instances = generate_all_instances(max_n=5)
    total = len(instances)
    passed = 0

    for idx, src in enumerate(instances, 1):
        # Validate source (will raise if malformed)
        try:
            Clique.validate(src)
        except Exception as exc:
            print(f"Source instance validation failed at index {idx}: {exc}", file=sys.stderr)
            continue

        src_answer = solve_clique(src)
        # Apply reduction
        try:
            tgt = reduction(src)
        except Exception as exc:
            print(f"Reduction raised an exception at index {idx}: {exc}", file=sys.stderr)
            continue
        # Validate target
        try:
            IndependentSet.validate(tgt)
        except Exception as exc:
            print(f"Target instance validation failed at index {idx}: {exc}", file=sys.stderr)
            continue

        tgt_answer = solve_independent_set(tgt)
        if src_answer == tgt_answer:
            passed += 1
        else:
            print(
                f"Mismatch on instance {idx}: src_answer={src_answer}, tgt_answer={tgt_answer}\n"
                f"src={src}\n tgt={tgt}\n",
                file=sys.stderr,
            )

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    # Print a human‑readable summary
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
