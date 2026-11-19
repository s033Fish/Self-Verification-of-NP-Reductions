"""Automated tests for the Clique → VertexCover reduction.

The repository provides only validation helpers for the two problems and a
``reduce`` function.  In order to verify that the reduction is correct we
implement straightforward brute‑force solvers for both problems and then
exhaustively test small instances.

For each graph with up to 5 vertices we enumerate every possible edge set and
several values of ``k`` (including negative values and values larger than the
number of vertices).  For each instance we:

1. Validate the original instance using ``Clique.validate``.
2. Solve the instance with the brute‑force ``solve_clique``.
3. Apply ``reduce`` to obtain a VertexCover instance.
4. Validate the reduced instance using ``VertexCover.validate``.
5. Solve the reduced instance with ``solve_vertex_cover``.
6. Check that the two answers agree.

The script records the total number of tests and how many passed.  It writes a
``verdict.json`` file in the repository root with the required fields so that
the evaluation harness can read the result.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Any

from problems import Clique, VertexCover
from reduce import reduce as reduce_instance


def solve_clique(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for Clique.

    Returns ``True`` iff the graph contains a clique of size at least ``k``.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
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
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def solve_vertex_cover(instance: Dict[str, Any]) -> bool:
    """Brute‑force solver for VertexCover.

    Returns ``True`` iff there exists a vertex cover of size **at most** ``k``.
    """
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]

    # Edge cases from the problem statement
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True

    vertices = list(range(n))
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            covered = True
            for u, v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False


def generate_all_instances(max_n: int = 5) -> List[Dict[str, Any]]:
    """Generate every Clique instance with up to ``max_n`` vertices.

    For each ``n`` we iterate over all possible edge subsets and a range of ``k``
    values that includes negative numbers and numbers larger than ``n``.
    """
    instances: List[Dict[str, Any]] = []
    for n in range(max_n + 1):
        all_pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges: List[List[int]] = []
            for i, (u, v) in enumerate(all_pairs):
                if mask & (1 << i):
                    edges.append([u, v])
            for k in range(-2, n + 3):
                instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    instances = generate_all_instances(max_n=5)
    total = len(instances)
    passed = 0

    for idx, inst in enumerate(instances, 1):
        try:
            Clique.validate(inst)
        except Exception as exc:
            print(f"Instance {idx}/{total} failed validation: {exc}", file=sys.stderr)
            continue
        source_ans = solve_clique(inst)
        reduced = reduce_instance(inst)
        try:
            VertexCover.validate(reduced)
        except Exception as exc:
            print(f"Reduced instance {idx}/{total} invalid: {exc}", file=sys.stderr)
            continue
        target_ans = solve_vertex_cover(reduced)
        if source_ans == target_ans:
            passed += 1
        else:
            print(f"Mismatch on instance {idx}/{total}: source={source_ans}, target={target_ans}", file=sys.stderr)

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
