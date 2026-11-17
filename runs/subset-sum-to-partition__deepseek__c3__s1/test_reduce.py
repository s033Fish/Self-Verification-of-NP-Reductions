import random

from problems import SOURCE, TARGET
from reduce import reduce


def check(instance):
    TARGET.validate(reduce(instance))
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduce(instance))
    assert expected == got, (instance, reduce(instance), expected, got)


def main():
    tests = 0

    # Exhaustive small instances.
    for scale in range(0, 6):
        for inst in SOURCE.enumerate_instances(scale):
            check(inst)
            tests += 1

    # Explicit edge cases.
    edge = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -1},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 0},
        {"numbers": [5], "target": 3},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 5},
        {"numbers": [1, 2, 3], "target": 4},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [1, 2, 3], "target": -5},
        {"numbers": [10**18, 10**18 + 1], "target": 10**18},
        {"numbers": [10**18, 10**18 + 1], "target": 10**18 + 1},
        {"numbers": [10**18, 10**18 + 1], "target": 2 * 10**18 + 1},
        {"numbers": [7, 7, 7], "target": 14},
        {"numbers": [7, 7, 7], "target": 21},
        {"numbers": [7, 7, 7], "target": 1},
    ]
    for inst in edge:
        check(inst)
        tests += 1

    # Randomized instances.
    rng = random.Random(12345)
    for _ in range(3000):
        scale = rng.randint(0, 9)
        inst = SOURCE.random_instance(rng, scale)
        check(inst)
        tests += 1

    print(f"ALL TESTS PASSED: {tests}")
    return tests


if __name__ == "__main__":
    main()
