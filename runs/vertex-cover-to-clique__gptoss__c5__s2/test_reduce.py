"""Test suite for the VertexCover → Clique reduction.

The repository provides a ``reduce`` function that transforms a VertexCover
instance into a Clique instance.  This file implements independent brute‑force
solvers for both problems and checks that the reduction preserves the answer
on a large number of randomly generated small instances.

The script writes a ``verdict.json`` file with the following fields:

* ``verified`` – ``true`` iff every test passed.
* ``tests_run`` – total number of generated source instances.
* ``tests_passed`` – number of instances where the reduction behaved correctly.

The test harness is deliberately lightweight and does not rely on any third‑
party libraries – only the standard library and the local ``problems`` and
``reduce`` modules.
"""

from __future__ import annotations

import json
import random
import itertools
from typing import List, Dict

from problems import VertexCover, Clique, InvalidInstance
from reduce import reduce as reduce_instance


def brute_vertex_cover(instance: Dict) -> bool:
    """Return ``True`` iff the VertexCover instance has a cover of size ≤ k.

    The implementation enumerates all subsets of vertices up to ``k`` and
    checks whether every edge is incident to at least one vertex in the subset.
    ``k`` may be negative – in that case the answer is always ``False`` as per
    the problem definition.
    """
    VertexCover.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = {frozenset(edge) for edge in edges if edge[0] in subset or edge[1] in subset}
            if len(covered) == len(edges):
                return True
    return False


def brute_clique(instance: Dict) -> bool:
    """Return ``True`` iff the Clique instance has a clique of size ≥ k.

    The function enumerates all subsets of vertices of size ``k`` up to ``n``
    and checks whether the induced subgraph is complete.
    """
    Clique.validate(instance)
    n = instance["n"]
    edges_set = {frozenset(edge) for edge in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    for s in range(k, n + 1):
        for subset in itertools.combinations(vertices, s):
            if all(frozenset((u, v)) in edges_set for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def random_instance(max_n: int = 6) -> Dict:
    """Generate a random VertexCover instance with ``n`` ≤ ``max_n``.

    The graph is created by randomly adding each possible edge with probability
    0.5.  ``k`` is chosen uniformly from ``[-1, n + 1]`` to also hit edge cases.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges: List[List[int]] = []
    for u, v in possible_edges:
        if random.random() < 0.5:
            edges.append([u, v])
    k = random.randint(-1, n + 1)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    tests_run = 0
    tests_passed = 0
    for _ in range(200):
        src = random_instance()
        try:
            VertexCover.validate(src)
        except InvalidInstance:
            continue
        src_answer = brute_vertex_cover(src)
        tgt = reduce_instance(src)
        tgt_answer = brute_clique(tgt)
        tests_run += 1
        if src_answer == tgt_answer:
            tests_passed += 1
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

if __name__ == "__main__":
    main()
