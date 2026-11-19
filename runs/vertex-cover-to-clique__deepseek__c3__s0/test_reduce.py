"""Tests comparing Vertex Cover brute force with the reduction to Clique."""

import random

from problems import SOURCE, TARGET
from reduce import reduce


def check(instance):
    reduced = reduce(instance)
    # The reduction must produce a valid target instance.
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert got == expected, (
        f"mismatch for {instance}: source={expected}, "
        f"reduced={reduced}, target={got}"
    )
    return reduced


def main():
    tests_run = 0

    # Exhaustive small instances: all graphs up to 4 vertices with all k.
    for scale in range(0, 5):
        for instance in SOURCE.enumerate_instances(scale):
            n = instance["n"]
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": instance["edges"], "k": k}
                SOURCE.validate(inst)
                check(inst)
                tests_run += 1

    # Random instances at slightly larger scales.
    rng = random.Random(12345)
    for _ in range(3000):
        scale = rng.randint(0, 9)
        instance = SOURCE.random_instance(rng, scale)
        check(instance)
        tests_run += 1

    # Explicit edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 5},
        {"n": 1, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
    ]
    for inst in edge_cases:
        SOURCE.validate(inst)
        check(inst)
        tests_run += 1

    print(f"all {tests_run} tests passed")
    return tests_run


if __name__ == "__main__":
    main()
