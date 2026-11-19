"""Tests for the 1-in-3-SAT -> Exact Cover reduction."""

import random

from problems import SOURCE, TARGET
from reduce import reduce


def check(instance, results):
    TARGET.validate(reduce(instance))
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduce(instance))
    results["run"] += 1
    if expected == got:
        results["passed"] += 1
    else:
        results["failures"].append((instance, expected, got))


def main():
    results = {"run": 0, "passed": 0, "failures": []}

    # 1. Exhaustive enumeration of all small formulas.
    for scale in range(4):
        for instance in SOURCE.enumerate_instances(scale):
            check(instance, results)

    # 2. Random instances over a range of scales.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(300):
            instance = SOURCE.random_instance(rng, scale)
            check(instance, results)

    # 3. Hand-crafted edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [3, 4, 2]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [1, 4, 5], [2, 4, 6], [3, 5, 6]]},
    ]
    for instance in edge_cases:
        SOURCE.validate(instance)
        check(instance, results)

    print(f"tests run:    {results['run']}")
    print(f"tests passed: {results['passed']}")
    for failure in results["failures"][:10]:
        print("FAILURE:", failure)
    assert not results["failures"], "reduction mismatch found"
    return results


if __name__ == "__main__":
    main()
