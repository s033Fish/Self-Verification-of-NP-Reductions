"""Independent tests for reduce.py: 3-SAT -> Subset Sum.

We implement brute-force solvers from the problem definitions and compare
the answer of each small source instance with the answer of its reduction.
"""
import itertools
import random
import sys

sys.path.insert(0, ".")
from reduce import reduce
from problems import ThreeSat, SubsetSum


# ----------------------------------------------------------------------
# Brute-force solvers (written from the definitions in problems.py)
# ----------------------------------------------------------------------

def solve_three_sat(instance):
    """Return True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1]
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance):
    """Return True iff some sub-list sums exactly to target.

    Meet-in-the-middle so it works even when the target is huge.
    """
    target = instance["target"]
    if target < 0:
        return False
    nums = [a for a in instance["numbers"] if a != 0]
    if target == 0:
        return True
    if len(nums) > 40:
        raise ValueError("instance too large for the brute-force test solver")

    def all_sums(arr):
        sums = [0]
        for a in arr:
            sums += [s + a for s in sums]
        return sums

    half = len(nums) // 2
    left = all_sums(nums[:half])
    right = set(all_sums(nums[half:]))
    return any((target - s) in right for s in left)


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_three_sat(rng, max_vars=5, max_clauses=6):
    m = rng.randint(0, max_vars)
    if m < 3:
        clauses = []
    else:
        n = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(n):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def dense_three_sat(rng, m, n):
    """Many clauses over few variables: often unsatisfiable."""
    clauses = []
    for _ in range(n):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def guaranteed_unsat(rng, m, triple, extra):
    """All 8 sign patterns on `triple` (unsat), plus `extra` random clauses."""
    a, b, c = triple
    clauses = [
        [s1 * a, s2 * b, s3 * c]
        for s1, s2, s3 in itertools.product([1, -1], repeat=3)
    ]
    for _ in range(extra):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    rng.shuffle(clauses)
    return {"num_vars": m, "clauses": clauses}


def all_three_sat_instances(max_vars=4, max_clause_subset=4):
    """Exhaustive small instances: clause subsets over all sign patterns."""
    yield {"num_vars": 0, "clauses": []}
    yield {"num_vars": 1, "clauses": []}
    yield {"num_vars": 2, "clauses": []}
    for m in range(3, max_vars + 1):
        all_clauses = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                all_clauses.append([s * v for s, v in zip(signs, vs)])
        for r in range(0, min(len(all_clauses), max_clause_subset) + 1):
            for subset in itertools.combinations(all_clauses, r):
                yield {"num_vars": m, "clauses": [list(c) for c in subset]}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(inst)
        expected = solve_three_sat(inst)
        red = reduce(inst)
        SubsetSum.validate(red)
        got = solve_subset_sum(red)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, inst, expected, got))

    # Exhaustive small instances
    for i, inst in enumerate(all_three_sat_instances(4, 4)):
        check(inst, f"exhaustive-{i}")

    # Random sparse instances
    rng = random.Random(12345)
    for i in range(300):
        check(random_three_sat(rng), f"random-{i}")

    # Dense random instances
    for i in range(200):
        m = rng.randint(3, 4)
        n = rng.randint(6, 8)
        check(dense_three_sat(rng, m, n), f"dense-{i}")

    # Guaranteed-unsatisfiable instances (the "no" side).
    for i in range(200):
        m = rng.randint(3, 5)
        triple = rng.sample(range(1, m + 1), 3)
        check(guaranteed_unsat(rng, m, triple, rng.randint(0, 4)), f"unsat-{i}")

    # Explicit known-unsatisfiable cases.
    unsat = {
        "num_vars": 3,
        "clauses": [
            [s1 * 1, s2 * 2, s3 * 3]
            for s1, s2, s3 in itertools.product([1, -1], repeat=3)
        ],
    }
    check(unsat, "explicit-unsat")
    check({"num_vars": 3, "clauses": list(reversed(unsat["clauses"]))}, "explicit-unsat-rev")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, inst, exp, got in failures[:5]:
            print(f"  {label}: expected {exp}, got {got}")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
