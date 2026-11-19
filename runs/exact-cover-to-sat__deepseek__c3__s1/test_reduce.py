import random
import itertools

import problems
from problems import ExactCover, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    # Validate source instance and reduction output.
    ExactCover.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = ExactCover.is_yes(instance)
    got = Sat.is_yes(out)
    assert got == expected, (
        f"MISMATCH on {instance!r}: source={expected}, reduced={got}, out={out!r}"
    )
    tests_passed += 1


def exhaustive_small():
    # Enumerate every collection of distinct subsets for u = 0..3.
    for universe_size in range(0, 4):
        all_subsets = [
            list(subset)
            for size in range(universe_size + 1)
            for subset in itertools.combinations(range(universe_size), size)
        ]
        for mask in range(1 << len(all_subsets)):
            sets = [s for i, s in enumerate(all_subsets) if mask >> i & 1]
            check({"universe_size": universe_size, "sets": sets})


def exhaustive_with_duplicates():
    # Small universe, allow duplicates and empty sets.
    universe_size = 2
    pool = [[], [0], [1], [0, 1]]
    for r in range(0, 5):
        for combo in itertools.product(pool, repeat=r):
            check({"universe_size": universe_size, "sets": list(combo)})


def random_tests(n=3000):
    rng = random.Random(12345)
    for _ in range(n):
        scale = rng.randint(0, 6)
        instance = ExactCover.random_instance(rng, scale)
        check(instance)


def edge_cases():
    # u = 0, no sets -> yes
    check({"universe_size": 0, "sets": []})
    # u = 0, some sets -> yes
    check({"universe_size": 0, "sets": [[], []]})
    # element with no covering set -> no
    check({"universe_size": 2, "sets": [[0]]})
    # duplicate non-empty sets cannot both be chosen
    check({"universe_size": 1, "sets": [[0], [0]]})
    # exact cover using one of duplicates
    check({"universe_size": 2, "sets": [[0], [0], [1]]})
    # empty clause case: element uncovered
    check({"universe_size": 3, "sets": [[0, 1], [1, 2]]})


if __name__ == "__main__":
    exhaustive_small()
    exhaustive_with_duplicates()
    random_tests()
    edge_cases()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
