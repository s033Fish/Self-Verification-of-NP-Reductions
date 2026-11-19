"""Tests for the Clique -> Vertex Cover reduction in reduce.py."""

import random

import problems
from problems import SOURCE, TARGET, enumerate_graphs_with_k
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    reduced = reduce(instance)
    # The reduction must output a valid target instance.
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert expected == got, (
        f"mismatch on {instance}: source={expected}, reduced={reduced}, "
        f"target={got}"
    )
    tests_passed += 1


def test_exhaustive():
    # Every graph on 0..4 vertices, every k from -1 to n+1 (edge cases).
    for instance in enumerate_graphs_with_k(4):
        check(instance)


def test_exhaustive_n5():
    # All 1024 graphs on 5 vertices with all relevant k.
    for instance in enumerate_graphs_with_k(5):
        check(instance)


def test_random():
    rng = random.Random(12345)
    for _ in range(2000):
        scale = rng.randint(0, 8)
        instance = SOURCE.random_instance(rng, scale)
        check(instance)


def test_edge_cases():
    # Explicit edge cases.
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 1},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 3},
        {"n": 3, "edges": [], "k": 4},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 5},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": -3},
    ]
    for instance in cases:
        SOURCE.validate(instance)
        check(instance)


def main():
    test_edge_cases()
    test_exhaustive()
    test_exhaustive_n5()
    test_random()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
