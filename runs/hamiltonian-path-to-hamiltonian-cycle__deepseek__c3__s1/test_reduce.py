import random

import problems
from problems import SOURCE, TARGET
from reduce import reduce


def check(instance):
    problems.HamiltonianPath.validate(instance)
    reduced = reduce(instance)
    problems.HamiltonianCycle.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert expected == got, (instance, reduced, expected, got)
    return expected


def main():
    tests_run = 0
    tests_passed = 0

    # Exhaustive over all labelled graphs for small n.
    for n in range(0, 6):
        for edges in problems.all_graphs(n):
            instance = {"n": n, "edges": edges}
            tests_run += 1
            check(instance)
            tests_passed += 1

    # Random instances at larger scales.
    rng = random.Random(12345)
    for scale in range(1, 11):
        for _ in range(60):
            instance = SOURCE.random_instance(rng, scale)
            tests_run += 1
            check(instance)
            tests_passed += 1

    # A few hand-picked edge cases.
    hand = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
    ]
    for instance in hand:
        tests_run += 1
        check(instance)
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
