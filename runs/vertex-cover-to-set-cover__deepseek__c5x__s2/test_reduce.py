"""Tests for the reduction from VertexCover to SetCover.

The test suite generates a number of small random instances of the source
problem (Vertex Cover), validates them using the provided ``validate``
method, runs the reduction, validates the produced target instance and then
compares the answers of brute‑force solvers for both problems.

The reduction is considered correct if for every generated instance the
answers agree.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from pathlib import Path

# Import the problem definitions and the reduction implementation.
import problems  # type: ignore
import reduce  # type: ignore


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the VertexCover instance has a cover of size at most k.

    The instance is assumed to be valid according to ``VertexCover.validate``.
    """
    n: int = instance["n"]
    edges: list[list[int]] = instance["edges"]
    k: int = instance["k"]

    if k < 0:
        return False
    if not edges:
        return True  # empty graph is always covered
    if k >= n:
        return True

    vertices = range(n)
    for r in range(k + 1):
        for subset in combinations(vertices, r):
            subset_set = set(subset)
            if all(u in subset_set or v in subset_set for u, v in edges):
                return True
    return False


def set_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the SetCover instance can be covered with ≤ k sets."""
    universe_size: int = instance["universe_size"]
    sets: list[list[int]] = instance["sets"]
    k: int = instance["k"]

    if k < 0:
        return False
    if universe_size == 0:
        return True

    universe = set(range(universe_size))
    for r in range(k + 1):
        for idx_subset in combinations(range(len(sets)), r):
            covered = set()
            for idx in idx_subset:
                covered.update(sets[idx])
            if covered >= universe:
                return True
    return False


def generate_random_vertex_cover_instance(max_n: int = 5) -> dict:
    """Generate a random valid VertexCover instance with small size.

    The number of vertices ``n`` is chosen uniformly from 0..max_n. All possible
    edges are considered and a random subset is taken. ``k`` is chosen from a
    range that includes negative values and values larger than ``n`` to test
    edge cases.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for e in possible_edges:
        if random.choice([True, False]):
            edges.append(list(e))
    k = random.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    # Exhaustive enumeration for tiny graphs (n <= 3).
    for n in range(0, 4):
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for edge_mask in range(1 << len(possible_edges)):
            edges = [list(possible_edges[i]) for i in range(len(possible_edges)) if (edge_mask >> i) & 1]
            for k in range(-1, n + 2):
                instance = {"n": n, "edges": edges, "k": k}
                problems.VertexCover.validate(instance)
                src_ans = vertex_cover_bruteforce(instance)
                tgt_instance = reduce.reduce(instance)
                problems.SetCover.validate(tgt_instance)
                tgt_ans = set_cover_bruteforce(tgt_instance)
                total += 1
                if src_ans == tgt_ans:
                    passed += 1
                else:
                    print("Mismatch!", instance, tgt_instance, src_ans, tgt_ans, file=sys.stderr)
    # Additional random tests.
    for _ in range(200):
        instance = generate_random_vertex_cover_instance(max_n=5)
        problems.VertexCover.validate(instance)
        src_ans = vertex_cover_bruteforce(instance)
        tgt_instance = reduce.reduce(instance)
        problems.SetCover.validate(tgt_instance)
        tgt_ans = set_cover_bruteforce(tgt_instance)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Random mismatch!", instance, tgt_instance, src_ans, tgt_ans, file=sys.stderr)

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
