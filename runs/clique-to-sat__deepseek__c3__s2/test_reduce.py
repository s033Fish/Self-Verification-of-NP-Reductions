"""Tests for the Clique -> SAT reduction in reduce.py."""

import random

import problems
from problems import Clique, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    Clique.validate(instance)
    out = reduce(instance)
    # The reduction must produce a valid SAT instance.
    Sat.validate(out)
    expected = Clique.is_yes(instance)
    got = Sat.is_yes(out)
    assert expected == got, (
        f"mismatch on {instance!r}: Clique={expected}, reduced SAT={got}, "
        f"formula={out!r}"
    )
    tests_passed += 1


def main():
    # 1. Exhaustive small graphs with every relevant k.
    for scale in range(0, 5):
        for instance in Clique.enumerate_instances(scale):
            n = instance["n"]
            for k in range(-2, n + 3):
                check({"n": n, "edges": instance["edges"], "k": k})

    # 2. Random instances of a few sizes.
    rng = random.Random(12345)
    for scale in range(0, 8):
        for _ in range(40):
            instance = Clique.random_instance(rng, scale)
            check(instance)

    # 3. Hand-picked edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 0, "edges": [], "k": -5})
    check({"n": 1, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 2})
    # Triangle graph: clique of size 3.
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4})
    # Path graph: max clique 2.
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 3})
    # Complete graph K5.
    complete = [[u, v] for u in range(5) for v in range(u + 1, 5)]
    for k in range(-1, 7):
        check({"n": 5, "edges": complete, "k": k})

    # 4. Larger random instances (still brute-forceable).
    for _ in range(20):
        instance = Clique.random_instance(rng, 10)
        check(instance)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
