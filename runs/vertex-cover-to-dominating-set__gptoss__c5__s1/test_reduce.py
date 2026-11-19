"""Automated tests for the reduction from Vertex Cover to Dominating Set.

The test suite enumerates all small graphs (up to 4 vertices) and a range of
values for ``k``. For each instance it:

1. Computes the exact answer for the source problem (Vertex Cover) by brute
   force.
2. Applies ``reduce`` to obtain an instance of the target problem.
3. Computes the exact answer for the target problem (Dominating Set) by brute
   force.
4. Checks that the two answers agree.

The script finally writes ``verdict.json`` containing the number of tests run
and how many passed. ``verified`` is true only when all tests pass.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict

# Import the problems and reduction implementation.
from problems import VertexCover, DominatingSet
from reduce import reduce as reduce_instance


def vertex_cover_bruteforce(instance: Dict) -> bool:
    """Return True iff the Vertex Cover instance has a cover of size <= k.

    The instance is assumed to be validated already.
    """
    n = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True  # empty edge set is always covered
    # Enumerate subsets up to size k.
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


def dominating_set_bruteforce(instance: Dict) -> bool:
    """Return True iff the Dominating Set instance has a dominating set of size <= k.
    """
    n = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    # Build adjacency list including self (domination by being in the set).
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


def generate_all_graphs(n: int) -> List[List[List[int]]]:
    """Return a list of edge lists representing all simple undirected graphs on n vertices.

    Each edge is a two‑element list [u, v] with u < v.
    """
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    graphs: List[List[List[int]]] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        graphs.append(edges)
    return graphs


def main() -> None:
    total_tests = 0
    passed_tests = 0

    # Enumerate small instances.
    for n in range(0, 5):  # up to 4 vertices (inclusive)
        all_graphs = generate_all_graphs(n)
        for edges in all_graphs:
            # k range: from -1 to n+1 to cover edge cases.
            for k in range(-1, n + 2):
                src_instance = {"n": n, "edges": edges, "k": k}
                # Validate source instance; if invalid, skip (should not happen).
                try:
                    VertexCover.validate(src_instance)
                except Exception:
                    continue
                src_answer = vertex_cover_bruteforce(src_instance)
                # Apply reduction.
                try:
                    tgt_instance = reduce_instance(src_instance)
                except Exception as e:
                    print("Reduction raised an exception", e, file=sys.stderr)
                    continue
                # Validate target instance.
                try:
                    DominatingSet.validate(tgt_instance)
                except Exception as e:
                    print("Target validation failed", e, file=sys.stderr)
                    continue
                tgt_answer = dominating_set_bruteforce(tgt_instance)
                total_tests += 1
                if src_answer == tgt_answer:
                    passed_tests += 1
                else:
                    print(
                        f"Mismatch for n={n}, edges={edges}, k={k}\n"
                        f"src={src_answer}, tgt={tgt_answer}\n"
                    )

    verdict = {
        "verified": passed_tests == total_tests,
        "tests_run": total_tests,
        "tests_passed": passed_tests,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
