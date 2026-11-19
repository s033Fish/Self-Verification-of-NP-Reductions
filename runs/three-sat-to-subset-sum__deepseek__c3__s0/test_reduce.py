"""Tests for reduce.py: compare brute-force solvers on small instances."""
import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    if expected != got:
        print("MISMATCH")
        print("  source:", instance)
        print("  reduced:", reduced)
        print("  expected:", expected, "got:", got)
        return False
    tests_passed += 1
    return True


def main():
    ok = True

    # 1. Hand-picked edge cases.
    edge = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 5, "clauses": []},
        # single clause, satisfiable
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        # single clause, all negated
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        # unsatisfiable: all 8 clauses over 3 vars
        {"num_vars": 3, "clauses": [
            [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
            [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]},
        # repeated clause
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        # variables unused
        {"num_vars": 6, "clauses": [[1, 2, 3]]},
        # unsat over 4 vars: every 3-subset, all sign patterns (needs 4 vars)
        {"num_vars": 4, "clauses": [
            [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
            [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]},
    ]
    for inst in edge:
        ok &= check(inst)

    # 2. Every small formula with num_vars <= 3 (distinct clauses).
    count = 0
    for inst in SOURCE.enumerate_instances(3):
        ok &= check(inst)
        count += 1
    print("enumerated formulas (scale 3):", count)

    # 3. Random instances across small scales (kept small so the brute-force
    #    subset-sum solver stays fast).
    rng = random.Random(12345)
    for scale in range(0, 8):
        for _ in range(40):
            inst = SOURCE.random_instance(rng, scale)
            ok &= check(inst)

    # 4. Random instances with a moderate number of variables/clauses.
    for scale in range(3, 8):
        for _ in range(15):
            inst = SOURCE.random_instance(rng, scale)
            ok &= check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
