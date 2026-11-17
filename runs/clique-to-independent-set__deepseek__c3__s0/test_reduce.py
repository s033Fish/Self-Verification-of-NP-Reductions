import random

import problems
from problems import Clique, IndependentSet
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1

    # The reduction must produce a valid target instance.
    IndependentSet.validate(reduce(instance))

    expected = Clique.is_yes(instance)
    got = IndependentSet.is_yes(reduce(instance))
    if expected != got:
        raise AssertionError(
            "mismatch on %r: Clique=%r IndependentSet(reduce)=%r"
            % (instance, expected, got)
        )
    TESTS_PASSED += 1


def main():
    # Exhaustive over all graphs on 0..5 vertices with every k in 0..n.
    for instance in Clique.enumerate_instances(5):
        check(instance)

    # Extra k values covering the edge cases (negative, k > n).
    for instance in Clique.enumerate_instances(4):
        for extra_k in (-3, -1, instance["n"] + 1, instance["n"] + 5):
            alt = dict(instance)
            alt["k"] = extra_k
            check(alt)

    # Random larger instances.
    rng = random.Random(12345)
    for scale in (6, 7, 8, 10, 15):
        for _ in range(200):
            check(Clique.random_instance(rng, scale))

    # A few hand-picked cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4})
    check({"n": 4, "edges": [], "k": 4})
    check({"n": 4, "edges": [], "k": 5})

    print("tests_run=%d tests_passed=%d" % (TESTS_RUN, TESTS_PASSED))
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
