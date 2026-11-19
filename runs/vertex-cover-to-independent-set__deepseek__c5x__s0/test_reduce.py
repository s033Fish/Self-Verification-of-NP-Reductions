"""Tests for the reduction from VertexCover to IndependentSet.

The repository provides only validation helpers for the problem instances.
We implement simple exhaustive solvers for both problems and then generate
random small instances to compare the answer of a source instance with the
answer of its reduced target instance.

If all generated tests agree, we consider the reduction verified.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from pathlib import Path

# Import the problem definitions and the reduction implementation.
import problems  # noqa: F401 – ensures validation code is available
from reduce import reduce


def solve_vertex_cover(instance: dict) -> bool:
    """Brute‑force solver for Vertex Cover.

    Returns True iff there exists a vertex cover of size at most ``k``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    # Edge cases from the problem statement.
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers all edges
    if k >= n:
        return True

    vertices = list(range(n))
    # Check all subsets of size up to k.
    for size in range(k + 1):
        for subset in combinations(vertices, size):
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

    Returns True iff there exists an independent set of size at least ``k``.
    """
    n = instance["n"]
    edges = {(u, v) for u, v in instance["edges"]}
    edges.update({(v, u) for u, v in edges})
    k = instance["k"]

    # Edge cases from the problem statement.
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True

    vertices = list(range(n))
    # Check all subsets of size >= k.
    for size in range(k, n + 1):
        for subset in combinations(vertices, size):
            subset_set = set(subset)
            independent = True
            for u, v in edges:
                if u in subset_set and v in subset_set:
                    independent = False
                    break
            if independent:
                return True
    return False


def random_graph(max_n: int = 6, edge_prob: float = 0.4) -> dict:
    """Generate a random graph instance with fields ``n``, ``edges``.
    ``k`` is left unspecified – callers add it.
    """
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    # Run a reasonable number of random tests.
    for _ in range(200):
        src = random_graph()
        # Choose k in a range that covers negative, zero, and larger values.
        k = random.randint(-2, src["n"] + 2)
        src["k"] = k
        # Validate source instance using the provided validator.
        try:
            problems.VertexCover.validate(src)
        except Exception as exc:
            print("Invalid source instance:", src, file=sys.stderr)
            raise

        tgt = reduce(src)
        # Validate target instance.
        try:
            problems.IndependentSet.validate(tgt)
        except Exception as exc:
            print("Invalid target instance:", tgt, file=sys.stderr)
            raise

        src_ans = solve_vertex_cover(src)
        tgt_ans = solve_independent_set(tgt)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("FAILURE", json.dumps({"src": src, "tgt": tgt, "src_ans": src_ans, "tgt_ans": tgt_ans}), file=sys.stderr)

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

