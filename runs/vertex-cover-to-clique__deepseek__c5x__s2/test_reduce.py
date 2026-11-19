"""Test the correctness of the reduction from VertexCover to Clique.

The script enumerates all small graph instances (up to 5 vertices) and
all possible values of ``k``. For each instance it:

1. Computes the exact answer for VertexCover by brute force.
2. Applies the provided ``reduce`` function.
3. Computes the exact answer for Clique on the reduced instance.
4. Checks that the two answers agree.

It finally writes a ``verdict.json`` file containing the number of tests run,
the number passed and whether the reduction is verified.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import VertexCover, Clique
from reduce import reduce as reduce_instance


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the VertexCover instance has a cover of size <= k.

    Implements the definition directly by checking all subsets of vertices.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    # Edge cases from the problem statement
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers all edges
    if k >= n:
        return True
    # Check subsets up to size k
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
    """Return True iff the Clique instance has a clique of size >= k."""
    n = instance["n"]
    edges_set = {frozenset((u, v)) for u, v in instance["edges"]}
    k = instance["k"]
    # Edge cases from the problem statement
    if k <= 0:
        return True
    if n == 0:
        return False  # k>0 cannot be satisfied
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    # We need at least k vertices, try all subsets of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # check if every pair is an edge
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def generate_all_instances(max_n: int = 5):
    """Yield all possible VertexCover instances with up to ``max_n`` vertices.

    For each ``n`` we iterate over every possible edge subset and every ``k``
    in the range ``[-1, n + 1]`` to cover edge cases.
    """
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u, v in itertools.combinations(vertices, 2)]
        for edge_mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if (edge_mask >> i) & 1:
                    edges.append([u, v])
            for k in range(-1, n + 2):  # include values below 0 and above n
                instance = {"n": n, "edges": edges, "k": k}
                # Validate using the problem's validator (may raise)
                try:
                    VertexCover.validate(instance)
                except Exception:
                    # Skip malformed instances (should not happen)
                    continue
                yield instance


def main() -> None:
    total = 0
    passed = 0
    for vc_instance in generate_all_instances():
        total += 1
        vc_answer = vertex_cover_bruteforce(vc_instance)
        # Apply reduction
        try:
            clique_instance = reduce_instance(vc_instance)
        except Exception as e:
            print(f"Reduction raised an exception on instance {vc_instance}: {e}", file=sys.stderr)
            continue
        # Verify target instance is valid
        try:
            Clique.validate(clique_instance)
        except Exception as e:
            print(f"Reduced instance invalid: {clique_instance}\nError: {e}", file=sys.stderr)
            continue
        clique_answer = clique_bruteforce(clique_instance)
        if vc_answer == clique_answer:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("VertexCover instance:", vc_instance, file=sys.stderr)
            print("VertexCover answer:", vc_answer, file=sys.stderr)
            print("Reduced Clique instance:", clique_instance, file=sys.stderr)
            print("Clique answer:", clique_answer, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
