"""Tests for the reduction from VertexCover to IndependentSet.

The repository provides only validation functions for the two problems.
This file implements tiny brute‑force solvers for both problems and then
exhaustively checks that ``reduce`` preserves the answer on a large number
of random small instances.

The script records how many tests were executed and how many passed and
writes a ``verdict.json`` file required by the task description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from typing import Dict, Any, List

from problems import VertexCover, IndependentSet
from reduce import reduce as reduce_instance


def vertex_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the VertexCover instance is a YES instance.

    Implements the definition directly by enumerating all subsets of
    vertices.  Works only for very small graphs (n <= 10) which is fine for
    our testing purposes.
    """
    n = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if not edges:
        return True  # empty edge set is covered by empty set for any k>=0
    if k >= n:
        return True

    vertices = list(range(n))
    # enumerate subsets up to size k
    for r in range(k + 1):
        for subset in combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def independent_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the IndependentSet instance is a YES instance.

    Brute‑forces all subsets of vertices and checks the independent set
    condition.
    """
    n = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k = instance["k"]

    # Edge cases from definition
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True  # any set of size k is independent

    vertices = list(range(n))
    # enumerate subsets of size >= k (we can stop early when we find one)
    for r in range(k, n + 1):
        for subset in combinations(vertices, r):
            subset_set = set(subset)
            independent = True
            for u, v in edges:
                if u in subset_set and v in subset_set:
                    independent = False
                    break
            if independent:
                return True
    return False


def random_instance(max_n: int = 6) -> Dict[str, Any]:
    """Generate a random VertexCover instance.

    n is chosen uniformly from 0..max_n.  Each possible edge is included with
    probability 0.3.  k is chosen from -1 .. n+1 to hit edge cases.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges: List[List[int]] = []
    for u, v in possible_edges:
        if random.random() < 0.3:
            edges.append([u, v])
    k = random.randint(-1, n + 1)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(500):  # enough to get good confidence
        src = random_instance()
        # Validate source (should pass). If it fails, our generator is buggy.
        try:
            VertexCover.validate(src)
        except Exception as e:
            print("Generated invalid source instance", src, file=sys.stderr)
            raise
        # Reduce
        tgt = reduce_instance(src)
        # Validate target
        IndependentSet.validate(tgt)

        src_ans = vertex_cover_bruteforce(src)
        tgt_ans = independent_set_bruteforce(tgt)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, tgt, src_ans, tgt_ans, file=sys.stderr)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
