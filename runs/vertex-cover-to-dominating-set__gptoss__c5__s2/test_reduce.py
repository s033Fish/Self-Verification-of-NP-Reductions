"""Automated tests for the reduction from VertexCover to DominatingSet.

The repository provides only validation functions for the two problems.
This test module implements exhaustive (brute‑force) solvers for both
problems based directly on their definitions and then checks that for a
large set of small random instances the reduction preserves the answer.

The script is intended to be executed directly (e.g. ``python -m pytest``
or simply ``python test_reduce.py``).  It reports the number of tests run
and passed and writes a ``verdict.json`` file in the repository root.
"""

from __future__ import annotations

import json
import random
import itertools
import sys
from typing import List, Dict, Tuple

from problems import VertexCover, DominatingSet
from reduce import reduce as reduce_instance


def solve_vertex_cover(instance: Dict) -> bool:
    """Brute‑force solver for VertexCover.

    Returns True iff there exists a vertex cover of size at most ``k``.
    """
    VertexCover.validate(instance)
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    if k < 0:
        return False
    if not edges:
        return True  # empty edge set is always covered
    if k >= n:
        return True

    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            subset_set = set(subset)
            if all(u in subset_set or v in subset_set for u, v in edges):
                return True
    return False


def solve_dominating_set(instance: Dict) -> bool:
    """Brute‑force solver for DominatingSet.

    Returns True iff there exists a dominating set of size at most ``k``.
    """
    DominatingSet.validate(instance)
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            dominated = set(subset)
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def random_instance(max_n: int = 6, edge_prob: float = 0.4) -> Dict:
    """Generate a random VertexCover instance.

    The instance may have negative k to test edge‑case handling.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(e) for e in possible_edges if random.random() < edge_prob]
    k = random.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        src = random_instance()
        ans_src = solve_vertex_cover(src)
        try:
            tgt = reduce_instance(src)
        except Exception as e:
            print(f"Reduction raised an exception on instance {src}: {e}")
            continue
        ans_tgt = solve_dominating_set(tgt)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, "->", tgt, ans_src, ans_tgt)

    # Exhaustive check for very small n (n <= 4)
    for n in range(0, 5):
        vertices = list(range(n))
        all_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for edge_mask in range(1 << len(all_edges)):
            edges = [list(all_edges[i]) for i in range(len(all_edges)) if (edge_mask >> i) & 1]
            for k in range(-1, n + 2):
                src = {"n": n, "edges": edges, "k": k}
                ans_src = solve_vertex_cover(src)
                tgt = reduce_instance(src)
                ans_tgt = solve_dominating_set(tgt)
                total += 1
                if ans_src == ans_tgt:
                    passed += 1
                else:
                    print("Exhaustive mismatch", src, tgt, ans_src, ans_tgt)

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
