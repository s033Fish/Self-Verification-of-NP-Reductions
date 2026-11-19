"""Tests comparing brute-force answers on 3-Coloring and its reduction."""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeColoring, IndependentSet
from reduce import reduce


def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable (brute force)."""
    n = instance["n"]
    edges = instance["edges"]
    for assignment in itertools.product(range(3), repeat=n):
        if all(assignment[u] != assignment[v] for u, v in edges):
            return True
    return False


def solve_independent_set(instance: dict) -> bool:
    """True iff there is an independent set of size >= k (brute force)."""
    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u not in chosen or v not in chosen for u, v in edges):
                return True
    return False


def all_graphs(n: int):
    """All simple undirected graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def random_graph(rng: random.Random, n: int, p: float) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeColoring.validate(instance)
        expected = solve_three_coloring(instance)
        reduced = reduce(instance)
        IndependentSet.validate(reduced)
        got = solve_independent_set(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((instance, expected, reduced, got))

    # Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})  # K4
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]})  # K5

    # Exhaustive over all graphs up to 4 vertices (2^6 = 64 at n=4).
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # Random graphs with up to 6 vertices (reduced IS has up to 18 vertices,
    # but k = n keeps the search small since triangles bound the max set).
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 6)
        p = rng.choice([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        check(random_graph(rng, n, p))

    # Random 3-colourable graphs built from random colourings.
    for _ in range(300):
        n = rng.randint(0, 7)
        colour = [rng.randrange(3) for _ in range(n)]
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if colour[u] != colour[v] and rng.random() < 0.5:
                    edges.append([u, v])
        check({"n": n, "edges": edges})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:5]:
            print(f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
