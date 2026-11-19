"""Tests for the 1-in-3-SAT -> Subset Sum reduction in reduce.py."""

import itertools
import random
import sys

import problems
from reduce import reduce

SOURCE = problems.OneInThreeSat
TARGET = problems.SubsetSum

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print(f"FAIL {label}: source={instance}")
        print(f"     reduced={reduced}")
        print(f"     expected={expected} got={got}")
        return False
    return True


def main():
    ok = True

    # 1. Edge cases.
    ok &= check({"num_vars": 0, "clauses": []}, "empty m=0")
    for m in range(0, 5):
        ok &= check({"num_vars": m, "clauses": []}, f"no clauses m={m}")

    # 2. Exhaustive small formulas: all subsets of clauses over small m.
    for m in range(3, 6):
        all_clauses = [list(c) for c in itertools.combinations(range(1, m + 1), 3)]
        # limit the number of clauses to keep 2^n manageable
        limit = min(len(all_clauses), 8)
        for r in range(0, limit + 1):
            for chosen in itertools.combinations(range(limit), r):
                clauses = [all_clauses[i] for i in chosen]
                ok &= check({"num_vars": m, "clauses": clauses}, f"exhaustive m={m}")

    # 3. Repeated clauses.
    for m in range(3, 6):
        for _ in range(50):
            clauses = []
            for _ in range(random.randint(1, 5)):
                c = sorted(random.sample(range(1, m + 1), 3))
                clauses.append(c)
                if random.random() < 0.4:
                    clauses.append(list(c))  # duplicate
            ok &= check({"num_vars": m, "clauses": clauses}, f"repeats m={m}")

    # 4. Random instances from the problem generator.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(60):
            inst = SOURCE.random_instance(rng, scale)
            ok &= check(inst, f"random scale={scale}")

    # 5. Larger random instances (still brute-forceable via the solvers).
    for scale in range(9, 13):
        for _ in range(15):
            inst = SOURCE.random_instance(rng, scale)
            ok &= check(inst, f"random large scale={scale}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if not ok or tests_passed != tests_run:
        print("SOME TESTS FAILED")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
