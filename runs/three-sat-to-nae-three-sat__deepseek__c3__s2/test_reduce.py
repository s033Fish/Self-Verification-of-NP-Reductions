"""Tests for the 3-SAT -> NAE-3-SAT reduction."""
import itertools
import random

import problems
from problems import ThreeSat, NaeThreeSat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    out = reduce(instance)
    NaeThreeSat.validate(out)  # must be a valid target instance
    expected = ThreeSat.is_yes(instance)
    got = NaeThreeSat.is_yes(out)
    ok = expected == got
    if ok:
        tests_passed += 1
    else:
        print(f"FAIL {label}: {instance} -> {out}: expected {expected} got {got}")
    return ok


def all_three_sat_formulas(num_vars, max_clauses=None):
    """All formulas over num_vars with distinct clauses (small)."""
    all_clauses = [
        [sign * v for sign, v in zip(signs, variables)]
        for variables in itertools.combinations(range(1, num_vars + 1), 3)
        for signs in itertools.product((1, -1), repeat=3)
    ]
    if max_clauses is not None:
        all_clauses = all_clauses[:max_clauses]
    for mask in range(1 << len(all_clauses)):
        yield {
            "num_vars": num_vars,
            "clauses": [c for i, c in enumerate(all_clauses) if mask >> i & 1],
        }


def main():
    # Edge cases: no clauses, various m.
    for m in range(0, 6):
        check({"num_vars": m, "clauses": []}, f"empty m={m}")

    # Exhaustive over all formulas with num_vars <= 3 (all 3-literal clauses).
    for m in (3,):
        for inst in all_three_sat_formulas(m):
            check(inst, "exhaustive m=3")

    # Exhaustive over all formulas with num_vars = 4 but limited clause set.
    for inst in all_three_sat_formulas(4, max_clauses=8):
        check(inst, "exhaustive m=4 partial")

    # Random instances of many sizes.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(300):
            inst = ThreeSat.random_instance(rng, scale)
            check(inst, f"random scale={scale}")

    # Random instances with duplicated clauses and unused variables.
    for _ in range(500):
        m = rng.randint(3, 7)
        n = rng.randint(1, 12)
        clauses = []
        for _ in range(n):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        if clauses:
            clauses.append(list(clauses[0]))  # duplicate
        check({"num_vars": m, "clauses": clauses}, "duplicates")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
