"""Tests for the Vertex Cover -> Set Cover reduction.

Includes brute-force solvers for both problems (written from the problem
definitions) and exhaustively compares them on many small instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import SetCover, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written directly from the definitions.

def vertex_cover_bruteforce(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def set_cover_bruteforce(instance: dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True
    # Any element in no set -> impossible.
    covered_by_any = set()
    for s in sets:
        covered_by_any.update(s)
    if covered_by_any != set(range(u)):
        return False
    limit = min(k, len(sets))
    for size in range(0, limit + 1):
        for combo in itertools.combinations(range(len(sets)), size):
            covered = set()
            for i in combo:
                covered.update(sets[i])
            if len(covered) == u:
                return True
    return False


# ----------------------------------------------------------------------
# Helpers to enumerate small Vertex Cover instances.

def all_graphs(n: int):
    """All simple graphs on n labelled vertices (as edge lists)."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield edges


def random_graph(n: int, p: float, rng: random.Random):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def check_instance(instance: dict) -> bool:
    """Validate, reduce, and compare both solvers. Returns True if consistent."""
    VertexCover.validate(instance)
    reduced = reduce(instance)
    SetCover.validate(reduced)
    src = vertex_cover_bruteforce(instance)
    tgt = set_cover_bruteforce(reduced)
    assert src == tgt, (instance, reduced, src, tgt)
    return True


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            if check_instance(instance):
                tests_passed += 1
        except AssertionError as exc:
            print("FAIL:", exc)

    # Exhaustive small graphs: n = 0..4, all edge sets, all k in -2..n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                run({"n": n, "edges": edges, "k": k})

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 7)
        edges = random_graph(n, rng.random(), rng)
        k = rng.randint(-2, n + 2)
        run({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    run({"n": 0, "edges": [], "k": 0})
    run({"n": 0, "edges": [], "k": -1})
    run({"n": 5, "edges": [], "k": 0})
    run({"n": 5, "edges": [], "k": -1})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})
    run({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1})
    run({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})

    # Structural checks on the reduction itself.
    inst = {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1}
    red = reduce(inst)
    assert red == {"universe_size": 2, "sets": [[0], [0, 1], [1]], "k": 1}, red
    # k is preserved exactly.
    for k in (-3, -1, 0, 5):
        assert reduce({"n": 2, "edges": [[0, 1]], "k": k})["k"] == k
    tests_run += 1
    tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
