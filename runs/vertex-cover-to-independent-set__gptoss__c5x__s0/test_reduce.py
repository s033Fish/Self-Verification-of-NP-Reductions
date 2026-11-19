"""Independent tests for reduce.py: Vertex Cover -> Independent Set.

We implement our own brute-force solvers directly from the problem
definitions in problems.py (which provides only validate()), generate many
small source instances, reduce each one, and compare the source answer with
the target answer.
"""

from __future__ import annotations

import itertools
import random
from typing import Any, Dict, List

from problems import VertexCover, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.
# ----------------------------------------------------------------------


def _edges_as_pairs(instance: Dict[str, Any]) -> List[tuple]:
    return [(u, v) for u, v in instance["edges"]]


def solve_vertex_cover(instance: Dict[str, Any]) -> bool:
    """True iff graph has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = _edges_as_pairs(instance)
    k = instance["k"]

    # Edge cases from the definition.
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True  # empty set covers it for any k >= 0

    # Try every subset of size 0..k.
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_independent_set(instance: Dict[str, Any]) -> bool:
    """True iff graph has an independent set of AT LEAST k vertices."""
    n = instance["n"]
    edges = _edges_as_pairs(instance)
    k = instance["k"]

    # Edge cases from the definition.
    if k <= 0:
        return True
    if k > n:
        return False

    # Try every subset of size k..n (only need to find one independent set).
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(not (u in chosen and v in chosen) for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation.
# ----------------------------------------------------------------------


def all_graphs(n: int):
    """Yield every simple undirected graph on n vertices as an edge list."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield edges


def make_instance(n: int, edges: List[List[int]], k: int) -> Dict[str, Any]:
    return {"n": n, "edges": [list(e) for e in edges], "k": k}


def random_instance(rng: random.Random, max_n: int = 6) -> Dict[str, Any]:
    n = rng.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = [list(e) for e in possible if rng.random() < 0.5]
    k = rng.randint(-2, n + 2)
    return make_instance(n, edges, k)


# ----------------------------------------------------------------------
# Test driver.
# ----------------------------------------------------------------------


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures: List[str] = []

    def check(instance: Dict[str, Any], label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Both problems must accept the instance format.
        VertexCover.validate(instance)
        src = solve_vertex_cover(instance)
        target = reduce(instance)
        IndependentSet.validate(target)
        tgt = solve_independent_set(target)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append(
                f"{label}: instance={instance} source={src} target={target} tgt={tgt}"
            )

    # 1) Exhaustive: all graphs on n = 0..4 vertices, k in -2..n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check(make_instance(n, edges, k), f"exhaustive n={n} k={k}")

    # 2) Random small instances, including larger n.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng, max_n=7), "random")

    # 3) Targeted edge cases.
    edge_cases = [
        make_instance(0, [], -1),
        make_instance(0, [], 0),
        make_instance(0, [], 5),
        make_instance(3, [], -1),
        make_instance(3, [], 0),
        make_instance(3, [], 3),
        make_instance(3, [], 10),
        make_instance(3, [[0, 1], [1, 2], [0, 2]], -1),
        make_instance(3, [[0, 1], [1, 2], [0, 2]], 0),
        make_instance(3, [[0, 1], [1, 2], [0, 2]], 1),
        make_instance(3, [[0, 1], [1, 2], [0, 2]], 2),
        make_instance(3, [[0, 1], [1, 2], [0, 2]], 3),
        make_instance(3, [[0, 1], [1, 2], [0, 2]], 4),
        make_instance(4, [[0, 1], [2, 3]], 1),
        make_instance(4, [[0, 1], [2, 3]], 2),
        make_instance(4, [[0, 1], [2, 3]], 3),
        make_instance(5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], 2),
        make_instance(5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], 3),
    ]
    for i, inst in enumerate(edge_cases):
        check(inst, f"edge-case {i}")

    # 4) Confirm the reduction output shape is exactly the target format.
    for inst in edge_cases:
        t = reduce(inst)
        assert set(t.keys()) == {"n", "edges", "k"}, t
        assert t["n"] == inst["n"]
        assert t["edges"] == inst["edges"]
        assert t["k"] == inst["n"] - inst["k"]

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print(" ", f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
