"""Automated tests for the VertexCover → Clique reduction.

The repository provides only validation helpers for the two problems and a
`reduce` function.  This test suite implements brute‑force solvers for both
problems, generates a number of random small instances, runs the reduction and
checks that the answers agree.  It also exercises several edge‑case instances
explicitly.

The script prints a JSON object compatible with the required ``verdict.json``
format: ``{"verified": <bool>, "tests_run": <int>, "tests_passed": <int>}``.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from typing import List, Dict, Any, Set

import problems  # provides VertexCover and Clique classes with .validate
from reduce import reduce as reduce_instance


def all_subsets(iterable: List[int]):
    """Yield all subsets of ``iterable`` as lists.

    The order is not important; the function is used only for exhaustive
    search on very small graphs (n ≤ 6) where 2ⁿ is cheap.
    """
    items = list(iterable)
    for r in range(len(items) + 1):
        for combo in combinations(items, r):
            yield list(combo)


def vertex_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph has a vertex cover of size at most ``k``.

    The implementation follows the definition verbatim: it checks every
    subset of vertices and returns True as soon as it finds a covering set
    whose cardinality does not exceed ``k``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True  # empty edge set is always covered

    vertices = list(range(n))
    for subset in all_subsets(vertices):
        if len(subset) > k:
            continue
        covered = True
        for u, v in edges:
            if u not in subset and v not in subset:
                covered = False
                break
        if covered:
            return True
    return False


def clique_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the graph contains a clique of size at least ``k``.
    """
    n = instance["n"]
    edges_set: Set[frozenset[int]] = {frozenset((u, v)) for u, v in instance["edges"]}
    k = instance["k"]

    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False

    vertices = list(range(n))
    for size in range(k, n + 1):
        for combo in combinations(vertices, size):
            ok = True
            for u, v in combinations(combo, 2):
                if frozenset((u, v)) not in edges_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def generate_random_instance(max_n: int = 6) -> Dict[str, Any]:
    """Create a random VertexCover instance with small n for exhaustive testing.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for u, v in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n + 2)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num_random: int = 200) -> tuple[int, int, bool]:
    total = 0
    passed = 0
    ok = True

    edge_cases: List[Dict[str, Any]] = [
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 2, "edges": [[0, 1]], "k": -1},
        {"n": 2, "edges": [[0, 1]], "k": 0},
        {"n": 2, "edges": [[0, 1]], "k": 1},
        {"n": 2, "edges": [[0, 1]], "k": 2},
    ]

    for instance in edge_cases:
        total += 1
        try:
            problems.VertexCover.validate(instance)
        except Exception as e:
            print("Invalid VertexCover instance in edge case:", instance, e, file=sys.stderr)
            ok = False
            continue
        vc_ans = vertex_cover_bruteforce(instance)
        reduced = reduce_instance(instance)
        try:
            problems.Clique.validate(reduced)
        except Exception as e:
            print("Reduced instance invalid:", reduced, e, file=sys.stderr)
            ok = False
            continue
        clique_ans = clique_bruteforce(reduced)
        if vc_ans == clique_ans:
            passed += 1
        else:
            ok = False

    for _ in range(num_random):
        instance = generate_random_instance()
        total += 1
        try:
            problems.VertexCover.validate(instance)
        except Exception:
            continue
        vc_ans = vertex_cover_bruteforce(instance)
        reduced = reduce_instance(instance)
        try:
            problems.Clique.validate(reduced)
        except Exception:
            ok = False
            continue
        clique_ans = clique_bruteforce(reduced)
        if vc_ans == clique_ans:
            passed += 1
        else:
            ok = False

    return total, passed, ok

if __name__ == "__main__":
    total, passed, ok = run_tests()
    verdict = {"verified": ok, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
