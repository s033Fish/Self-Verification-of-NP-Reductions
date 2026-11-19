"""Test suite for the reduction from Independent Set to Clique.

The repository provides only the problem definitions and a purported
polynomial‑time reduction in ``reduce.py``.  To verify the reduction we
implement exhaustive (brute‑force) solvers for both source and target
problems and compare their answers on a large collection of small
instances.

The test enumerates all undirected graphs on ``n`` vertices for ``n`` up to
5 (which yields at most 2**10 = 1024 graphs) and a range of ``k`` values.
For each instance we:

1. Validate the source instance using ``IndependentSet.validate``.
2. Compute the answer with ``brute_independent_set``.
3. Apply ``reduce`` to obtain a target instance and validate it with
   ``Clique.validate``.
4. Compute the answer with ``brute_clique``.
5. Record whether the answers match.

At the end we write ``verdict.json`` containing the total number of tests
run, how many passed, and a ``verified`` flag that is true only if *all*
tests passed.
"""

from __future__ import annotations

import itertools
import json
import os
from typing import List, Tuple

from problems import IndependentSet, Clique
from reduce import reduce as reduce_instance


def brute_independent_set(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size at least k.

    The implementation enumerates all subsets of vertices.  For small n
    (<=5) this is perfectly fine.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k > n:
        return False

    # Enumerate subsets of vertices of size >= k
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Check if subset is independent
            independent = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    independent = False
                    break
            if independent:
                return True
    return False


def brute_clique(instance: dict) -> bool:
    """Return True iff the graph has a clique of size at least k.
    """
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]

    # Edge cases from the problem statement
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            # Check if every pair is an edge
            is_clique = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    is_clique = False
                    break
            if is_clique:
                return True
    return False


def generate_all_instances(max_n: int = 5) -> List[dict]:
    """Generate every possible graph up to ``max_n`` vertices.

    For each graph we also generate a range of ``k`` values covering the
    interesting edge cases: ``k`` from ``-1`` up to ``n+1``.
    """
    instances: List[dict] = []
    for n in range(max_n + 1):
        # All possible unordered edges (u < v)
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for edge_mask in range(1 << len(possible_edges)):
            edges: List[List[int]] = []
            for i, (u, v) in enumerate(possible_edges):
                if (edge_mask >> i) & 1:
                    edges.append([u, v])
            for k in range(-1, n + 2):  # includes k <= 0 and k > n
                instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    all_instances = generate_all_instances(max_n=5)
    total = len(all_instances)
    passed = 0

    for instance in all_instances:
        # Validate the source instance – should never raise.
        IndependentSet.validate(instance)
        src_answer = brute_independent_set(instance)

        # Apply reduction and validate target instance.
        target = reduce_instance(instance)
        Clique.validate(target)
        tgt_answer = brute_clique(target)

        if src_answer == tgt_answer:
            passed += 1
        else:
            pass

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
