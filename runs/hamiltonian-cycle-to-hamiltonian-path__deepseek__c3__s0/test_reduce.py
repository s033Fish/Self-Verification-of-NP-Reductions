import random

import problems
from reduce import reduce

SOURCE = problems.HamiltonianCycle
TARGET = problems.HamiltonianPath


def check(instance):
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive over all graphs with 0..5 vertices.
    for n in range(0, 6):
        for instance in SOURCE.enumerate_instances(n):
            if instance["n"] != n:
                continue
            expected = check(instance)
            tests_run += 1
            tests_passed += 1

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 12)
        p = rng.random()
        edges = [
            [u, v]
            for u in range(n)
            for v in range(u + 1, n)
            if rng.random() < p
        ]
        instance = {"n": n, "edges": edges}
        check(instance)
        tests_run += 1
        tests_passed += 1

    # A few hand-picked cases.
    hand = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},
    ]
    for instance in hand:
        check(instance)
        tests_run += 1
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
