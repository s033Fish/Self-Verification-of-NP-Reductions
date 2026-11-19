"""Automated tests for the reduction from VertexCover to DominatingSet.

The tests generate all small graph instances (up to 5 vertices) and a range
of ``k`` values, then compare the answer of a brute‑force solver for the
source problem with the answer for the target problem after applying the
reduction defined in ``reduce.py``.

If every comparison matches, the reduction is considered verified.
The script writes a ``verdict.json`` file containing the verification result
and statistics.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict

from problems import VertexCover, DominatingSet
from reduce import reduce as reduce_instance


def brute_vertex_cover(instance: Dict) -> bool:
    """Return True iff the VertexCover instance is a yes‑instance.

    The implementation follows the definition in ``problems.VertexCover``
    and checks all subsets of vertices (exponential but fine for tiny graphs).
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True  # empty graph is always covered by the empty set

    vertices = list(range(n))
    # iterate over subsets of size up to k
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


def brute_dominating_set(instance: Dict) -> bool:
    """Return True iff the DominatingSet instance is a yes‑instance.

    Checks all subsets of vertices up to ``k``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True
    if n == 0:
        return True

    # Build adjacency list including self (domination condition)
    adj: List[set[int]] = [set() for _ in range(n)]
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


def generate_all_instances(max_n: int = 5) -> List[Dict]:
    """Generate every graph up to ``max_n`` vertices with all possible edge sets.

    For each graph we also generate a selection of ``k`` values covering the
    interesting edge cases.
    """
    instances: List[Dict] = []
    for n in range(max_n + 1):
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for edge_mask in range(1 << len(possible_edges)):
            edges: List[List[int]] = []
            for i, (u, v) in enumerate(possible_edges):
                if edge_mask & (1 << i):
                    edges.append([u, v])
            for k in range(-1, n + 2):
                instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    instances = generate_all_instances(max_n=5)
    total = len(instances)
    passed = 0
    for src in instances:
        VertexCover.validate(src)
        src_answer = brute_vertex_cover(src)
        tgt = reduce_instance(src)
        DominatingSet.validate(tgt)
        tgt_answer = brute_dominating_set(tgt)
        if src_answer == tgt_answer:
            passed += 1
        else:
            print("Mismatch on instance:")
            print(json.dumps(src, indent=2))
            print("Reduced instance:")
            print(json.dumps(tgt, indent=2))
            print(f"src_answer={src_answer}, tgt_answer={tgt_answer}")
            sys.exit(1)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

