"""Automated tests for the reduction from VertexCover to Clique.

The repository provides a ``reduce`` function that transforms a VertexCover
instance into a Clique instance.  To verify its correctness we implement
brute‑force solvers for both problems and compare the answers on a variety
of small instances.

The script iterates over all graphs with up to ``MAX_N_EXHAUSTIVE`` vertices
and also runs a number of random instances with a slightly larger ``MAX_N``.
For each instance we:
  1. Compute the answer for VertexCover using ``vc_bruteforce``.
  2. Apply ``reduce`` to obtain a Clique instance.
  3. Compute the answer for Clique using ``clique_bruteforce``.
  4. Verify that the two answers are identical.

The results are written to ``verdict.json`` in the required format.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Any

from problems import VertexCover, Clique
from reduce import reduce


def vc_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the VertexCover instance is a YES instance.

    The implementation tries all subsets of vertices up to size ``k``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    # Edge cases according to the problem statement
    if k < 0:
        return False
    if not edges:
        return True  # empty edge set is always covered
    if k >= n:
        return True

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


def clique_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the Clique instance is a YES instance.

    Checks all subsets of size >= k for being a clique.
    """
    n = instance["n"]
    edges_set = {tuple(sorted(e)) for e in instance["edges"]}
    k = instance["k"]
    # Edge cases from the problem definition
    if k <= 0:
        return True
    if n == 0:
        return False  # k>0 cannot be satisfied
    if k == 1:
        return n >= 1
    if k > n:
        return False

    vertices = list(range(n))
    # We only need to check subsets of size exactly k up to n; early exit when found.
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if tuple(sorted((u, v))) not in edges_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def generate_all_instances(max_n: int) -> List[Dict[str, Any]]:
    """Generate every graph up to ``max_n`` vertices with every possible k.

    For each ``n`` we iterate over all edge subsets (the power set of the
    possible undirected edges) and over a range of ``k`` values from -1 to
    ``n + 1`` to cover edge cases.
    """
    instances: List[Dict[str, Any]] = []
    for n in range(max_n + 1):
        # all possible undirected edges without self‑loops
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(possible_edges)):
            edges: List[List[int]] = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            # k values: include negative, zero, up to n+1
            for k in range(-1, n + 2):
                instances.append({"n": n, "edges": edges, "k": k})
    return instances


def generate_random_instances(num: int, max_n: int) -> List[Dict[str, Any]]:
    """Generate ``num`` random instances with up to ``max_n`` vertices."""
    rnd = random.Random(0)
    instances: List[Dict[str, Any]] = []
    for _ in range(num):
        n = rnd.randint(0, max_n)
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges: List[List[int]] = []
        for u, v in possible_edges:
            if rnd.random() < 0.5:
                edges.append([u, v])
        k = rnd.randint(-2, n + 2)
        instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    # Exhaustive testing for small n (up to 5 vertices) – this is fast enough.
    exhaustive = generate_all_instances(max_n=5)
    # Additional random testing for n up to 7.
    random_cases = generate_random_instances(num=200, max_n=7)
    all_cases = exhaustive + random_cases

    tests_run = 0
    tests_passed = 0
    for instance in all_cases:
        # Validate source instance (should not raise).
        VertexCover.validate(instance)
        src_ans = vc_bruteforce(instance)
        reduced = reduce(instance)
        Clique.validate(reduced)
        tgt_ans = clique_bruteforce(reduced)
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            # Print a minimal failing case for debugging.
            print("FAILURE", file=sys.stderr)
            print("source", instance, file=sys.stderr)
            print("reduced", reduced, file=sys.stderr)
            print("src_ans", src_ans, "tgt_ans", tgt_ans, file=sys.stderr)
        tests_run += 1

    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
