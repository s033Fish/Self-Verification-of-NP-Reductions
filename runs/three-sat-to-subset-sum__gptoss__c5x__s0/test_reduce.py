"""Independent tests for reduce.py: 3-SAT -> Subset Sum.

We implement our own brute-force solvers from the problem definitions in
problems.py and compare them with the reduction on many small instances.
"""
import itertools
import random

from problems import ThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.
# ----------------------------------------------------------------------

def three_sat_solve(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(
            any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            )
            for clause in clauses
        ):
            return True
    return False


def subset_sum_solve(instance):
    """Return True iff some sub-list sums to the target (bitset DP)."""
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reach = 1  # bit s set means sum s is reachable
    for a in numbers:
        reach |= reach << a
    return (reach >> target) & 1 == 1


# ----------------------------------------------------------------------
# Instance generators (small).
# ----------------------------------------------------------------------

def all_clauses(m):
    out = []
    for combo in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([combo[i] * signs[i] for i in range(3)])
    return out


def random_instance(rng, m, max_clauses):
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v * rng.choice([1, -1]) for v in vs])
    return {"num_vars": m, "clauses": clauses}


def run():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = three_sat_solve(instance)
        reduced = reduce(instance)
        got = subset_sum_solve(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, expected, got))

    # Edge cases: no clauses.
    for m in range(0, 5):
        check({"num_vars": m, "clauses": []}, f"no clauses m={m}")

    # Edge case: m=0 with no clauses only (clauses need m>=3).
    check({"num_vars": 0, "clauses": []}, "m=0 no clauses")

    # Exhaustive over all formulas on 3 variables (2^8 subsets of clauses).
    cls3 = all_clauses(3)
    for r in range(len(cls3) + 1):
        for sub in itertools.combinations(cls3, r):
            check({"num_vars": 3, "clauses": [list(c) for c in sub]},
                  "exhaustive m=3")

    # Random instances for m = 3,4,5.
    rng = random.Random(12345)
    for m in (3, 4, 5):
        for _ in range(3000):
            check(random_instance(rng, m, max_clauses=6), f"random m={m}")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = run()
    print(f"tests_run={tests_run} tests_passed={tests_passed} "
          f"failures={len(failures)}")
    for label, inst, expected, got in failures[:10]:
        print("FAIL", label, inst, "sat=", expected, "subset_sum=", got)
    if failures:
        raise SystemExit(1)
