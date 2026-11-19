"""Automated tests for the reduction from VertexCover to IndependentSet.

The file defines brute‑force solvers for both problems, generates a large
number of small random instances, applies the provided ``reduce`` function
and checks that the answers agree.  At the end a ``verdict.json`` file is
written with the required fields.

The tests are deliberately lightweight – they only explore graphs with up to
6 vertices, which keeps the exhaustive search feasible (2⁶ = 64 subsets).
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from typing import Dict, List

# Import the reduction and problem classes from the repository.
from reduce import reduce as reduce_instance  # noqa: N813 (shadow built‑in)
from problems import VertexCover, IndependentSet, InvalidInstance


def vertex_cover_bruteforce(instance: Dict) -> bool:
    """Return ``True`` iff the instance has a vertex cover of size ≤ k.

    The implementation enumerates all subsets of vertices.  For each subset we
    check whether every edge has at least one endpoint in the subset and whether
    the subset size respects the bound ``k``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases from the problem statement.
    if k < 0:
        return False
    if not edges:
        return True  # empty edge set is always covered
    if k >= n:
        return True

    vertices = list(range(n))
    # Enumerate subsets in increasing size order – early exit possible.
    for size in range(k + 1):
        for subset in combinations(vertices, size):
            subset_set = set(subset)
            covered = True
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def independent_set_bruteforce(instance: Dict) -> bool:
    """Return ``True`` iff the instance has an independent set of size ≥ k.

    The function enumerates all subsets and checks that no edge is internal to
    the subset and that the subset size meets the bound ``k``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases from the problem statement.
    if k <= 0:
        return True
    if k > n:
        return False
    if not edges:
        return True  # any set of vertices is independent

    vertices = list(range(n))
    # Enumerate subsets of size at least k.
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


def random_instance(max_n: int = 6) -> Dict:
    """Generate a random VertexCover instance with ``n`` ≤ ``max_n``.

    The number of vertices ``n`` is chosen uniformly from 0..max_n.  For each
    unordered pair of vertices we include the edge with probability 0.5.  The
    bound ``k`` is drawn from ``[-2, n + 2]`` to cover edge‑cases.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(e) for e in possible_edges if random.random() < 0.5]
    k = random.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    total = 0
    passed = 0
    failures = []

    for _ in range(500):
        src = random_instance()
        try:
            VertexCover.validate(src)
        except InvalidInstance as exc:
            print(f"Generated invalid instance: {exc}", file=sys.stderr)
            continue
        src_answer = vertex_cover_bruteforce(src)
        try:
            tgt = reduce_instance(src)
        except Exception as exc:
            print(f"Reduction raised an exception: {exc}", file=sys.stderr)
            failures.append({"source": src, "error": str(exc)})
            total += 1
            continue
        try:
            IndependentSet.validate(tgt)
        except InvalidInstance as exc:
            print(f"Reduction produced invalid target: {exc}", file=sys.stderr)
            failures.append({"source": src, "target": tgt, "error": str(exc)})
            total += 1
            continue
        tgt_answer = independent_set_bruteforce(tgt)
        total += 1
        if src_answer == tgt_answer:
            passed += 1
        else:
            failures.append({"source": src, "target": tgt, "src_answer": src_answer, "tgt_answer": tgt_answer})

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
    if failures:
        print("\nFailures:", file=sys.stderr)
        for f in failures[:5]:
            print(json.dumps(f, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

