"""Brute-force solvers and tests for the Vertex Cover -> Independent Set reduction."""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, IndependentSet
from reduce import reduce


def brute_vertex_cover(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(u in s or v in s for u, v in edges):
                return True
    return False


def brute_independent_set(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(not (u in s and v in s) for u, v in edges):
                return True
    return False


def random_instance(rng, max_n=6):
    n = rng.randint(0, max_n)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [list(e) for e in all_edges[:m]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    # Exhaustive-ish random testing.
    for _ in range(3000):
        inst = random_instance(rng)
        VertexCover.validate(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        expected = brute_vertex_cover(inst)
        got = brute_independent_set(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", red, "expected", expected, "got", got)

    # Explicit edge cases.
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 5},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 3},
    ]
    for inst in cases:
        VertexCover.validate(inst)
        red = reduce(inst)
        IndependentSet.validate(red)
        expected = brute_vertex_cover(inst)
        got = brute_independent_set(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", red, "expected", expected, "got", got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
