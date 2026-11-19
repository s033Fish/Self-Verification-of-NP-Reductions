"""Tests for reduce.py: brute-force solvers + comparison on many instances."""
import itertools
import random

from problems import ThreeSat, NaeThreeSat
from reduce import reduce


def lit_true(lit, assign):
    return assign[abs(lit)] if lit > 0 else not assign[abs(lit)]


def solve_3sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assign = {i + 1: bits[i] for i in range(m)}
        if all(any(lit_true(l, assign) for l in c) for c in clauses):
            return True
    return False


def solve_nae(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        assign = {i + 1: bits[i] for i in range(m)}
        ok = True
        for c in clauses:
            vals = [lit_true(l, assign) for l in c]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


def random_instance(rng, max_m=6, max_n=6):
    m = rng.randint(3, max_m)
    n = rng.randint(0, max_n)
    clauses = []
    for _ in range(n):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    def check(inst, tag=""):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(inst)
        out = reduce(inst)
        NaeThreeSat.validate(out)
        a = solve_3sat(inst)
        b = solve_nae(out)
        if a == b:
            tests_passed += 1
        else:
            print("FAIL", tag, inst, "->", out, "src", a, "tgt", b)

    # Edge cases.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "empty m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "dup clause")
    # All 8 clauses over 3 vars -> unsatisfiable.
    all8 = []
    for signs in itertools.product([1, -1], repeat=3):
        all8.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    check({"num_vars": 3, "clauses": all8}, "all 8 clauses (unsat)")
    # 7 of 8 clauses -> satisfiable.
    check({"num_vars": 3, "clauses": all8[:-1]}, "7 clauses (sat)")

    # Random tests.
    for _ in range(400):
        check(random_instance(rng))

    # Exhaustive-ish: all single clauses for m=3.
    for signs in itertools.product([1, -1], repeat=3):
        check({"num_vars": 3, "clauses": [[signs[0] * 1, signs[1] * 2, signs[2] * 3]]},
              "single exhaustive")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
