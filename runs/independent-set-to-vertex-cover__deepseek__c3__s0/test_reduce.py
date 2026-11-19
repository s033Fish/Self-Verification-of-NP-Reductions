import random

import problems
from problems import SOURCE, TARGET
from reduce import reduce


def check(instance):
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert got == expected, (instance, reduced, expected, got)


def test_enumerated():
    count = 0
    for scale in range(0, 6):
        for instance in SOURCE.enumerate_instances(scale):
            check(instance)
            count += 1
    return count


def test_random():
    rng = random.Random(12345)
    count = 0
    for _ in range(3000):
        scale = rng.randint(0, 8)
        instance = SOURCE.random_instance(rng, scale)
        check(instance)
        count += 1
    return count


def test_edge_cases():
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 3},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 5, "edges": [], "k": -1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 0},
    ]
    for instance in cases:
        check(instance)
    return len(cases)


if __name__ == "__main__":
    total = 0
    total += test_enumerated()
    total += test_random()
    total += test_edge_cases()
    print(f"all tests passed: {total} instances")
