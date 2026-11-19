"""Tests comparing brute-force answers on small Vertex Cover instances
with the answers on their Set Cover reductions."""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, SetCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_vertex_cover(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
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
    target = set(range(u))
    for size in range(0, min(k, len(sets)) + 1):
        for combo in itertools.combinations(range(len(sets)), size):
            covered = set()
            for i in combo:
                covered.update(sets[i])
            if covered >= target:
                return True
    return False


# ----------------------------------------------------------------------
# Helpers to enumerate small graphs.

def all_graphs(n: int):
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield edges


def random_graph(rng: random.Random, n: int) -> list:
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < 0.5:
            edges.append([u, v])
    return edges


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        VertexCover.validate(instance)
        reduced = reduce(instance)
        SetCover.validate(reduced)
        expected = solve_vertex_cover(instance)
        got = solve_set_cover(reduced)
        assert expected == got, (
            f"mismatch on {instance}: vertex cover={expected}, "
            f"reduced={reduced}, set cover={got}"
        )
        tests_passed += 1

    # Exhaustive: all graphs on 0..4 vertices, all k from -1 to n+1.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-1, n + 2):
                check({"n": n, "edges": edges, "k": k})

    # Randomised larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 7)
        edges = random_graph(rng, n)
        k = rng.randint(-1, n + 1)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 5, "edges": [], "k": 0})
    check({"n": 5, "edges": [], "k": -1})
    check({"n": 5, "edges": [], "k": 3})
    check({"n": 3, "edges": [[0, 1]], "k": 0})
    check({"n": 3, "edges": [[0, 1]], "k": 1})
    check({"n": 3, "edges": [[0, 1]], "k": -5})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1})

    # Reversed edge orientation must give the same answer.
    check({"n": 3, "edges": [[1, 0], [2, 1]], "k": 1})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )


if __name__ == "__main__":
    main()
