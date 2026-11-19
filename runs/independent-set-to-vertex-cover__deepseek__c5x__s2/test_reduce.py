"""Test suite for the reduction from Independent Set to Vertex Cover.

The repository provides only validation for problem instances.  To verify the
correctness of ``reduce.py`` we implement straightforward brute‑force solvers
for both problems and compare the answers on many small random instances.

The test script performs the following steps:

1. Enumerate all graphs with up to ``MAX_N`` vertices (``MAX_N`` is kept small
   because the brute‑force solver is exponential).
2. For each graph enumerate a range of ``k`` values (including edge‑case
   values such as ``k <= 0`` and ``k > n``).
3. For each source instance compute the answer using ``solve_independent``.
4. Apply ``reduce`` to obtain a target instance and validate it with
   ``VertexCover.validate``.
5. Compute the answer for the target instance using ``solve_vertex_cover``.
6. Verify that the two answers match.

If any mismatch is found the script prints a diagnostic and exits with a
non‑zero status code.  At the end it prints a JSON object summarising the
result, which is later written to ``verdict.json`` by the main driver.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

from problems import IndependentSet, VertexCover
from reduce import reduce as reduce_instance


def solve_independent(instance: dict) -> bool:
    """Brute‑force check for an independent set of size at least k.

    Returns ``True`` iff the instance satisfies the Independent Set yes‑condition.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k > n:
        return False

    # Enumerate subsets of vertices of size >= k and test independence.
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            subset_set = set(subset)
            independent = True
            for u, v in edges:
                if u in subset_set and v in subset_set:
                    independent = False
                    break
            if independent:
                return True
    return False


def solve_vertex_cover(instance: dict) -> bool:
    """Brute‑force check for a vertex cover of size at most k.

    Returns ``True`` iff the instance satisfies the Vertex Cover yes‑condition.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if k >= n:
        return True

    vertices = list(range(n))
    # Enumerate subsets of size up to k and test if they cover all edges.
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            subset_set = set(subset)
            covers_all = all(u in subset_set or v in subset_set for u, v in edges)
            if covers_all:
                return True
    return False


def generate_all_graphs(max_n: int):
    """Yield all simple undirected graphs with vertices 0..max_n-1.

    Each graph is represented as a list of edges ``[[u, v], ...]`` where ``u < v``.
    """
    vertices = list(range(max_n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    for r in range(len(possible_edges) + 1):
        for edges in itertools.combinations(possible_edges, r):
            yield [[u, v] for u, v in edges]


def main() -> None:
    MAX_N = 5  # keep small to finish quickly
    tests_run = 0
    tests_passed = 0

    for n in range(0, MAX_N + 1):
        # enumerate all graphs on n vertices
        for edges in generate_all_graphs(n):
            # try a range of k values, covering edge cases
            ks = list(range(-2, n + 3))  # includes <0, 0..n, >n
            for k in ks:
                src_instance = {"n": n, "edges": edges, "k": k}
                # validate source instance (should be well‑formed)
                IndependentSet.validate(src_instance)

                src_ans = solve_independent(src_instance)
                tgt_instance = reduce_instance(src_instance)
                # validate reduced instance against target spec
                VertexCover.validate(tgt_instance)
                tgt_ans = solve_vertex_cover(tgt_instance)

                tests_run += 1
                if src_ans == tgt_ans:
                    tests_passed += 1
                else:
                    print("Mismatch detected:")
                    print("source", src_instance, "src_ans", src_ans)
                    print("target", tgt_instance, "tgt_ans", tgt_ans)
                    sys.exit(1)

    # All tests passed
    result = {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
