"""Tests: compare brute-force solvers on small 1-in-3-SAT instances and
their Exact Cover reductions."""

import random
import sys

import problems
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    want = SOURCE.is_yes(instance)
    got = TARGET.is_yes(out)
    if want == got:
        tests_passed += 1
    else:
        failures.append((label, instance, out, want, got))


def main():
    # 1) Exhaustive enumeration of all small formulas (num_vars <= 3).
    for scale in range(4):
        for inst in SOURCE.enumerate_instances(scale):
            check(inst, f"enumerate scale={scale}")

    # 2) Random instances of larger size.
    rng = random.Random(12345)
    for _ in range(400):
        scale = rng.randint(0, 7)
        inst = SOURCE.random_instance(rng, scale)
        check(inst, f"random scale={scale}")

    # 3) Hand-crafted edge cases.
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6]]},
        {"num_vars": 6, "clauses": [[1, 2, 3], [3, 4, 5], [5, 6, 1]]},
    ]
    for inst in edge:
        check(inst, "edge")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for label, inst, out, want, got in failures[:5]:
            print("FAIL", label, inst, "want", want, "got", got)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
