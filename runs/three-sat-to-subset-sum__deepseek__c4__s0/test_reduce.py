"""Tests for reduce.py: 3-SAT -> Subset Sum."""

import itertools
import random
import bisect
import json

from problems import ThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_sat(instance):
    """Return True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def _subset_sums(nums):
    sums = [0]
    for a in nums:
        sums = sums + [s + a for s in sums]
    return sums


def solve_subset_sum(instance):
    """Return True iff some sub-list sums to exactly target (meet in middle)."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    mid = len(numbers) // 2
    left = _subset_sums(numbers[:mid])
    right = sorted(_subset_sums(numbers[mid:]))
    for s in left:
        need = target - s
        i = bisect.bisect_left(right, need)
        if i < len(right) and right[i] == need:
            return True
    return False


def answers_agree(src_instance):
    reduced = reduce(src_instance)
    ThreeSat.validate(src_instance)
    SubsetSum.validate(reduced)
    return solve_three_sat(src_instance) == solve_subset_sum(reduced)


# ----------------------------------------------------------------------
# Test helpers.

tests_run = 0
tests_passed = 0


def check(name, condition):
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        print(f"FAIL: {name}")


# ----------------------------------------------------------------------
# Fixed edge cases.

check("no clauses m=0", answers_agree({"num_vars": 0, "clauses": []}))
check("no clauses m=5", answers_agree({"num_vars": 5, "clauses": []}))
check("single clause all pos", answers_agree({"num_vars": 3, "clauses": [[1, 2, 3]]}))
check("single clause all neg", answers_agree({"num_vars": 3, "clauses": [[-1, -2, -3]]}))
check("unsat 8 clauses", answers_agree({
    "num_vars": 3,
    "clauses": [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
    ],
}))
check("duplicate clauses", answers_agree({
    "num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]],
}))
check("unused vars", answers_agree({"num_vars": 6, "clauses": [[1, 2, 3]]}))
check("mixed", answers_agree({
    "num_vars": 4,
    "clauses": [[1, -2, 3], [-1, 2, -4], [2, 3, 4], [-3, -4, 1]],
}))

# ----------------------------------------------------------------------
# Randomized small instances.

rng = random.Random(12345)


def random_formula(max_vars=6, max_clauses=8):
    m = rng.randint(0, max_vars)
    k = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(k):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


for i in range(800):
    check(f"random {i}", answers_agree(random_formula()))

# Exhaustive-ish: 3-var formulas over a small clause pool.
pool = []
for vs in itertools.combinations([1, 2, 3], 3):
    for signs in itertools.product([1, -1], repeat=3):
        pool.append([v * s for v, s in zip(vs, signs)])

for trial in range(800):
    k = rng.randint(0, 5)
    clauses = [list(rng.choice(pool)) for _ in range(k)]
    check(f"pool {trial}", answers_agree({"num_vars": 3, "clauses": clauses}))

# ----------------------------------------------------------------------
# Structural checks: reduction output format and polynomial size.

inst = {"num_vars": 10, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 5, -6]]}
red = reduce(inst)
SubsetSum.validate(red)
check("number count", len(red["numbers"]) == 2 * 10 + 2 * 3)

print(f"tests_run={tests_run} tests_passed={tests_passed}")

with open("verdict.json", "w") as f:
    json.dump({"verified": tests_run == tests_passed,
               "tests_run": tests_run,
               "tests_passed": tests_passed}, f)
