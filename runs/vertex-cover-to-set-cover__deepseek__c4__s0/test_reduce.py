"""Tests for the Vertex Cover -> Set Cover reduction."""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, SetCover
from reduce import reduce
from solvers import vertex_cover_answer, set_cover_answer

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    VertexCover.validate(instance)
    reduced = reduce(instance)
    SetCover.validate(reduced)
    expected = vertex_cover_answer(instance)
    got = set_cover_answer(reduced)
    assert expected == got, (
        f"mismatch on {instance}: source={expected}, reduced={got}, "
        f"reduction={reduced}"
    )
    tests_passed += 1


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if mask >> i & 1]


def test_exhaustive_small() -> None:
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})


def test_edge_cases() -> None:
    # no edges
    for k in range(-2, 5):
        check({"n": 3, "edges": [], "k": k})
    # k < 0 always no
    check({"n": 2, "edges": [[0, 1]], "k": -1})
    # k >= n always yes
    check({"n": 2, "edges": [[0, 1]], "k": 5})
    # empty graph n = 0
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    # single edge
    check({"n": 2, "edges": [[0, 1]], "k": 0})
    check({"n": 2, "edges": [[0, 1]], "k": 1})


def test_random_medium() -> None:
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        rng.shuffle(pairs)
        m = rng.randint(0, len(pairs))
        edges = [list(p) for p in pairs[:m]]
        # randomly orient some edges
        edges = [e if rng.random() < 0.5 else [e[1], e[0]] for e in edges]
        k = rng.randint(-1, n + 1)
        check({"n": n, "edges": edges, "k": k})


def test_reduction_shape() -> None:
    inst = {"n": 4, "edges": [[0, 1], [1, 2], [3, 3 - 3]], "k": 2}
    # avoid self loop: fix
    inst = {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2}
    red = reduce(inst)
    assert red["universe_size"] == 3
    assert red["k"] == 2
    assert len(red["sets"]) == 4
    assert red["sets"][1] == [0, 1]
    assert red["sets"][0] == [0]
    assert red["sets"][3] == [2]
    global tests_run, tests_passed
    tests_run += 1
    tests_passed += 1


def main() -> None:
    test_exhaustive_small()
    test_edge_cases()
    test_random_medium()
    test_reduction_shape()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": tests_run == tests_passed,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
            },
            fh,
        )
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
