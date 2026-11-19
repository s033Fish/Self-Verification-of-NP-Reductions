"""Test the reduction from VertexCover to Clique.

This script implements brute‑force solvers for both problems based on the
formal definitions in ``problems.py``. It enumerates all small graph instances,
applies ``reduce`` and checks that the answer to the source instance matches
the answer to the reduced target instance.

The script also validates that both the original and reduced instances satisfy
their respective ``validate`` methods.

At the end it writes ``verdict.json`` with the fields required by the task
description.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import problems
from reduce import reduce


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True if the graph has a vertex cover of size at most k.

    Handles the edge cases described in the problem statement.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        # Empty graph is covered by empty set for any k >= 0
        return True

    vertices = list(range(n))
    # Try all subsets up to size k
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
    """Return True if the graph has a clique of size at least k.

    Handles the edge cases described in the problem statement.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    edge_set = {frozenset((u, v)) for u, v in edges}
    vertices = list(range(n))
    # Check all subsets of size >= k (we can stop early when found)
    for r in range(k, n + 1):
        for subset in itertools.combinations(vertices, r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edge_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def generate_all_instances(max_n: int = 5) -> list[dict]:
    """Generate all valid VertexCover instances for n up to ``max_n``.

    For each n we enumerate every possible edge subset (undirected, no loops)
    and a range of k values covering typical edge cases.
    """
    instances = []
    for n in range(max_n + 1):
        # all possible unordered pairs
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
            # Choose k values: a few around the extremes
            ks = set([-2, -1, 0, 1, n - 1, n, n + 1, n + 2])
            # also include a random middle value if n>0
            if n > 0:
                ks.add(n // 2)
            for k in ks:
                instance = {"n": n, "edges": edges, "k": k}
                # Validation may raise; we only keep valid ones
                try:
                    problems.VertexCover.validate(instance)
                except Exception:
                    continue
                instances.append(instance)
    return instances


def main() -> None:
    instances = generate_all_instances(max_n=5)
    total = len(instances)
    passed = 0
    for inst in instances:
        # Compute answers
        src_ans = vertex_cover_bruteforce(inst)
        # Apply reduction
        red_inst = reduce(inst)
        # Validate reduced instance as Clique
        try:
            problems.Clique.validate(red_inst)
        except Exception as e:
            print("Validation failed on reduced instance:", red_inst, file=sys.stderr)
            raise
        tgt_ans = clique_bruteforce(red_inst)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print("Source instance:", json.dumps(inst), file=sys.stderr)
            print("Reduced instance:", json.dumps(red_inst), file=sys.stderr)
            print("src_ans", src_ans, "tgt_ans", tgt_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()

