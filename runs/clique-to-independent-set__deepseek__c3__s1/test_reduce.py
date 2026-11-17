import random

from problems import SOURCE, TARGET
from reduce import reduce

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    out = reduce(instance)
    # The reduction must produce a valid target instance.
    TARGET.validate(out)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(out)
    assert got == expected, (instance, out, expected, got)
    TESTS_PASSED += 1


def main():
    rng = random.Random(12345)

    # Exhaustive small instances (all graphs on up to 4 vertices, all k).
    for instance in SOURCE.enumerate_instances(4):
        check(instance)

    # Random instances of larger scale.
    for _ in range(400):
        scale = rng.randint(0, 9)
        check(SOURCE.random_instance(rng, scale))

    # Edge cases: k <= 0, k > n, empty graphs, complete graphs.
    for n in range(0, 6):
        edges = [[u, v] for u in range(n) for v in range(u + 1, n)]
        for k in (-5, -1, 0, 1, n, n + 1, n + 5):
            check({"n": n, "edges": [], "k": k})
            check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
