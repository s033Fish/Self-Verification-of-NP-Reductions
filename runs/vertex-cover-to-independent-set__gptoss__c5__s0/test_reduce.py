"""Test suite for the reduction from VertexCover to IndependentSet.

The task requires us to verify that the provided ``reduce`` function
preserves the answer of the source problem.  To do this we implement
brute‑force solvers for both problems based directly on the definitions
in ``problems.py`` and then enumerate a large number of small instances.

For each instance we:
1. Compute the answer for VertexCover using ``solve_vertex_cover``.
2. Reduce the instance with ``reduce``.
3. Compute the answer for IndependentSet on the reduced instance using
   ``solve_independent_set``.
4. Check that the two answers are identical.

The script records how many tests were run and how many passed and writes
``verdict.json`` as required by the prompt.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import VertexCover, IndependentSet
from reduce import reduce as reduce_instance


def solve_vertex_cover(instance: dict) -> bool:
    """Brute‑force solver for Vertex Cover.

    Returns ``True`` iff the graph has a vertex cover of size at most ``k``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True  # empty set covers all edges

    # Enumerate all subsets of vertices up to size k
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


def solve_independent_set(instance: dict) -> bool:
    """Brute‑force solver for Independent Set.

    Returns ``True`` iff the graph has an independent set of size at least ``k``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    # Edge cases
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True

    vertices = list(range(n))
    # Iterate subsets of size >= k
    for r in range(k, n + 1):
        for subset in itertools.combinations(vertices, r):
            subset_set = set(subset)
            independent = True
            for u, v in edges:
                if u in subset_set and v in subset_set:
                    independent = False
                    break
            if independent:
                return True
    return False


def generate_all_instances(max_n: int = 5) -> list[dict]:
    """Generate a list of all valid VertexCover instances up to ``max_n``.

    For each ``n`` we consider every possible subset of the ``n*(n-1)/2``
    undirected edges and a range of ``k`` values covering the edge cases.
    """
    instances = []
    for n in range(max_n + 1):
        # All possible edges (u < v)
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for edge_subset in itertools.chain.from_iterable(
            itertools.combinations(possible_edges, r) for r in range(len(possible_edges) + 1)
        ):
            edges = [list(e) for e in edge_subset]
            # Choose k values that include edge cases and typical values
            k_values = set([-1, 0, 1, n - 1, n, n + 1])
            # Also include a few values around half of n
            k_values.update({n // 2, n // 2 - 1, n // 2 + 1})
            for k in k_values:
                instance = {"n": n, "edges": edges, "k": k}
                # Validate using the problem's validator to ensure we only keep
                # well‑formed instances.
                try:
                    VertexCover.validate(instance)
                except Exception:
                    continue
                instances.append(instance)
    return instances


def main() -> None:
    instances = generate_all_instances(max_n=4)  # keep runtime reasonable
    total = len(instances)
    passed = 0
    for idx, src in enumerate(instances, 1):
        src_answer = solve_vertex_cover(src)
        try:
            tgt = reduce_instance(src)
        except Exception as e:
            print(f"Reduction raised an exception on instance {idx}: {e}")
            continue
        tgt_answer = solve_independent_set(tgt)
        if src_answer == tgt_answer:
            passed += 1
        else:
            print("Mismatch detected!")
            print("Source instance:", src)
            print("Reduced instance:", tgt)
            print("VertexCover answer:", src_answer)
            print("IndependentSet answer:", tgt_answer)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()

