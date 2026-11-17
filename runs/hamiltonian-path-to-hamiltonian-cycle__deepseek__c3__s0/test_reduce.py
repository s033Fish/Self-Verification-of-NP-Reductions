"""Tests for the Hamiltonian Path -> Hamiltonian Cycle reduction.

Compares the brute-force solvers in problems.py on many small source
instances and their reductions.
"""

import random

import problems
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    """Validate + compare source and reduced answers."""
    global tests_run, tests_passed
    tests_run += 1

    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)

    src = SOURCE.is_yes(instance)
    tgt = TARGET.is_yes(reduced)
    assert src == tgt, (
        f"mismatch: source={src} target={tgt}\n"
        f"instance={instance}\nreduced={reduced}"
    )
    tests_passed += 1


def test_exhaustive():
    # Every graph on 0..5 vertices.
    for instance in SOURCE.enumerate_instances(5):
        check(instance)


def test_random():
    rng = random.Random(12345)
    for _ in range(400):
        scale = rng.randint(0, 9)
        check(SOURCE.random_instance(rng, scale))


def test_edge_cases():
    # n = 0: no
    check({"n": 0, "edges": []})
    # n = 1: yes
    check({"n": 1, "edges": []})
    # n = 2: yes iff edge present
    check({"n": 2, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    # n = 3: path yes, triangle yes
    check({"n": 3, "edges": [[0, 1], [1, 2]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    # n = 4: path but no cycle
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]})


def test_exhaustive_six():
    # Exhaustive over all graphs on 6 vertices (32768 instances).
    for instance in SOURCE.enumerate_instances(6):
        check(instance)


if __name__ == "__main__":
    test_edge_cases()
    test_exhaustive()
    test_random()
    test_exhaustive_six()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
