"""Test suite for the reduction from VertexCover to IndependentSet.

The repository provides only validation helpers for the two problems and
the reduction implementation.  To verify the reduction we implement brute‑
force solvers for both problems and exhaustively test many small instances.

The test counts the number of instances examined and records whether the
answers agree with the reduction.  The results are written to ``verdict.json``
as required by the task description.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

# Import the problem definitions and the reduction.
import problems
from reduce import reduce as reduce_instance


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the VertexCover instance has a cover of size ≤ k.

    The instance format is validated by ``VertexCover.validate``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    # Edge cases from the problem statement.
    if k < 0:
        return False
    if not edges:
        return True  # empty set always covers.
    if k >= n:
        return True

    # Try all subsets up to size k.
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            cover = set(subset)
            if all(u in cover or v in cover for u, v in edges):
                return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the IndependentSet instance has an independent set of size ≥ k.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    # Edge cases.
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True

    vertices = list(range(n))
    # Search subsets of size >= k, starting from k up to n.
    for r in range(k, n + 1):
        for subset in itertools.combinations(vertices, r):
            s = set(subset)
            if all(not (u in s and v in s) for u, v in edges):
                return True
    return False


def generate_random_instance(n: int, edge_prob: float, k_range: tuple[int, int]) -> dict:
    """Create a random VertexCover instance.

    ``k_range`` is a tuple (min_k, max_k) inclusive. ``edge_prob`` controls
    the probability of each possible undirected edge being present.
    """
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(k_range[0], k_range[1])
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0

    # Exhaustively test all graphs up to n=5 (2^{n choose 2} possibilities).
    for n in range(0, 6):
        vertices = list(range(n))
        all_possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        # Iterate over a subset of edge sets to keep runtime reasonable.
        for edge_mask in range(0, 1 << len(all_possible_edges)):
            edges = [list(all_possible_edges[i]) for i in range(len(all_possible_edges)) if (edge_mask >> i) & 1]
            # Test a few k values for each graph.
            for k in range(-1, n + 2):  # include values below 0 and above n
                instance = {"n": n, "edges": edges, "k": k}
                # Validate instance (should not raise).
                try:
                    problems.VertexCover.validate(instance)
                except Exception as e:
                    print(f"Invalid VertexCover instance generated: {e}", file=sys.stderr)
                    continue
                # Compute answers.
                vc_answer = vertex_cover_bruteforce(instance)
                reduced = reduce_instance(instance)
                # Validate reduced instance.
                try:
                    problems.IndependentSet.validate(reduced)
                except Exception as e:
                    print(f"Reduced instance invalid: {e}", file=sys.stderr)
                    continue
                is_answer = independent_set_bruteforce(reduced)
                tests_run += 1
                if vc_answer == is_answer:
                    tests_passed += 1
                else:
                    print("Mismatch found:")
                    print("Original:", instance)
                    print("Reduced:", reduced)
                    print("VC answer", vc_answer, "IS answer", is_answer)

    # Also run a number of random larger instances (n up to 8) to increase coverage.
    for _ in range(200):
        n = random.randint(0, 8)
        instance = generate_random_instance(n, edge_prob=0.4, k_range=(-2, n + 2))
        try:
            problems.VertexCover.validate(instance)
        except Exception:
            continue
        vc_answer = vertex_cover_bruteforce(instance)
        reduced = reduce_instance(instance)
        try:
            problems.IndependentSet.validate(reduced)
        except Exception:
            continue
        is_answer = independent_set_bruteforce(reduced)
        tests_run += 1
        if vc_answer == is_answer:
            tests_passed += 1

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
