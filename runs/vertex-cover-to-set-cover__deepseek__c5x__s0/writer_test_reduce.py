"""Tests for the Vertex Cover -> Set Cover reduction.

Includes brute-force solvers written from the problem definitions, plus
randomised and edge-case comparisons between source and reduced instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import SetCover, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)


def solve_vertex_cover(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for chosen in itertools.combinations(range(n), size):
            cover = set(chosen)
            if all(u in cover or v in cover for u, v in edges):
                return True
    return False


def solve_set_cover(instance: dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True
    for size in range(0, min(k, len(sets)) + 1):
        for chosen in itertools.combinations(range(len(sets)), size):
            covered = set()
            for i in chosen:
                covered.update(sets[i])
            if len(covered) == u:
                return True
    return False


# ----------------------------------------------------------------------
# Helpers


def check(instance: dict) -> bool:
    """Validate, reduce, validate target, and compare answers."""
    VertexCover.validate(instance)
    target = reduce(instance)
    SetCover.validate(target)
    a = solve_vertex_cover(instance)
    b = solve_set_cover(target)
    assert a == b, f"mismatch: source={a} target={b}\n{instance}\n{target}"
    return a


def random_instance(rng: random.Random, max_n: int = 6) -> dict:
    n = rng.randint(0, max_n)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [list(e) for e in all_edges[:m]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Tests


def test_edge_cases() -> int:
    count = 0
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 0, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [[0, 1]], "k": 0},
        {"n": 3, "edges": [[0, 1]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 0},
    ]
    for case in cases:
        check(case)
        count += 1
    return count


def test_random(trials: int = 3000, seed: int = 12345) -> int:
    rng = random.Random(seed)
    for _ in range(trials):
        check(random_instance(rng))
    return trials


def test_random_dense() -> int:
    """Exhaustive-ish over all graphs on up to 4 vertices with all k."""
    count = 0
    for n in range(0, 5):
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_edges)):
            edges = [list(all_edges[i]) for i in range(len(all_edges)) if mask >> i & 1]
            for k in range(-1, n + 2):
                check({"n": n, "edges": edges, "k": k})
                count += 1
    return count


def test_reduction_shape() -> int:
    """Check the structural properties of the reduction output."""
    count = 0
    instance = {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1}
    target = reduce(instance)
    assert target["universe_size"] == 2
    assert target["sets"] == [[0], [0, 1], [1]]
    assert target["k"] == 1
    count += 1
    # empty graph
    target = reduce({"n": 2, "edges": [], "k": 0})
    assert target == {"universe_size": 0, "sets": [[], []], "k": 0}
    count += 1
    # k is copied unchanged (including negatives)
    target = reduce({"n": 2, "edges": [[0, 1]], "k": -5})
    assert target["k"] == -5
    count += 1
    return count


def main() -> None:
    total = 0
    passed = 0
    tests = [
        ("edge_cases", test_edge_cases),
        ("random", test_random),
        ("random_dense", test_random_dense),
        ("reduction_shape", test_reduction_shape),
    ]
    for name, fn in tests:
        n = fn()
        total += n
        passed += n
        print(f"PASS {name}: {n} checks")
    print(f"TOTAL {passed}/{total}")
    assert passed == total


if __name__ == "__main__":
    main()
