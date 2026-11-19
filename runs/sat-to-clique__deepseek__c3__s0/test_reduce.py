import random

import problems
from problems import Sat, Clique
from reduce import reduce


def check(instance):
    out = reduce(instance)
    Sat.validate(instance)
    Clique.validate(out)
    src = Sat.is_yes(instance)
    tgt = Clique.is_yes(out)
    assert src == tgt, (instance, out, src, tgt)
    return 1


def main():
    tests = 0
    passed = 0

    # 1. Exhaustive small formulas (all clause subsets over <=3 vars).
    for scale in range(0, 3):
        for inst in Sat.enumerate_instances(scale):
            tests += 1
            check(inst)
            passed += 1

    # 2. Random instances of various scales.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(200):
            inst = Sat.random_instance(rng, scale)
            tests += 1
            check(inst)
            passed += 1

    # 3. Hand-crafted edge cases, including repeats and tautologies.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 1, "clauses": [[]]},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        {"num_vars": 1, "clauses": [[1, -1]]},
        {"num_vars": 2, "clauses": [[1, 1, 1]]},
        {"num_vars": 2, "clauses": [[1, 1], [-1, -1]]},
        {"num_vars": 2, "clauses": [[1, -1], [2, -2]]},
        {"num_vars": 2, "clauses": [[1], [1], [1]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2], [-1, 3], [-2, -3]]},
        {"num_vars": 3, "clauses": [[1], [-1], [2]]},
        {"num_vars": 4, "clauses": [[1, 2], [2, 3], [3, 4], [-1, -4]]},
        {"num_vars": 4, "clauses": [[1, -2], [2, -3], [3, -4], [4, -1]]},
        {"num_vars": 5, "clauses": [[1, 2, 3], [-1, -2], [3, 4], [-3, 5], [-4, -5]]},
    ]
    for inst in edge_cases:
        tests += 1
        check(inst)
        passed += 1

    # 4. Larger random instances (still brute-forceable).
    for scale in range(9, 13):
        for _ in range(30):
            inst = Sat.random_instance(rng, scale)
            tests += 1
            check(inst)
            passed += 1

    print(f"tests_run={tests} tests_passed={passed}")
    assert tests == passed
    return tests, passed


if __name__ == "__main__":
    main()
