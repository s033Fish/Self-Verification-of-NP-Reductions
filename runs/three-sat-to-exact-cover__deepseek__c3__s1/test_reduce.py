"""Tests comparing the brute-force 3-SAT and Exact Cover solvers on many
small source instances and their reductions."""

import itertools
import random
import sys

sys.path.insert(0, ".")

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    expected = SOURCE.is_yes(instance)
    reduced = reduce(instance)
    # The reduction must produce a valid TARGET instance.
    TARGET.validate(reduced)
    got = TARGET.is_yes(reduced)
    if expected == got:
        tests_passed += 1
        return True
    print("FAIL", instance, "expected", expected, "got", got)
    print("  reduced", reduced)
    return False


def all_clauses(num_vars):
    clauses = []
    for variables in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            clauses.append([sign * v for sign, v in zip(signs, variables)])
    return clauses


def main():
    # Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 1, "clauses": []})
    check({"num_vars": 7, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})

    # Exhaustive over every subset of the 8 clauses on variables 1..3.
    clauses = all_clauses(3)
    assert len(clauses) == 8
    for mask in range(1 << len(clauses)):
        instance = {
            "num_vars": 3,
            "clauses": [clauses[i] for i in range(len(clauses)) if mask >> i & 1],
        }
        check(instance)

    # Random instances with 4..6 variables.
    rng = random.Random(12345)
    for _ in range(4000):
        num_vars = rng.randint(3, 6)
        num_clauses = rng.randint(0, 12)
        clauses = []
        for _ in range(num_clauses):
            variables = rng.sample(range(1, num_vars + 1), 3)
            clauses.append(
                [v if rng.random() < 0.5 else -v for v in variables]
            )
        check({"num_vars": num_vars, "clauses": clauses})

    # Random instances from the problem's own generator.
    for scale in range(0, 7):
        for _ in range(200):
            check(SOURCE.random_instance(rng, scale))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
