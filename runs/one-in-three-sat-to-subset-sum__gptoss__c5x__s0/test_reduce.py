"""Independent tests for reduce.py: 1-in-3-SAT (positive) -> Subset Sum.

We implement our own brute-force solvers from the problem definitions and
compare answers on many small source instances.  At the end we write
verdict.json summarising the run.
"""
from __future__ import annotations

import itertools
import json
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)
# ----------------------------------------------------------------------

def solve_one_in_three_sat(instance) -> bool:
    """Exhaustive search over all assignments of variables 1..m."""
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            count = sum(1 for v in clause if bits[v - 1])
            if count != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance) -> bool:
    """Exhaustive search over all sub-lists (each position used at most once)."""
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    try:
        reduced = reduce(instance)
        SubsetSum.validate(reduced)  # target instance must be well formed
        src_ans = solve_one_in_three_sat(instance)
        tgt_ans = solve_subset_sum(reduced)
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append((label, instance, reduced, src_ans, tgt_ans))
    except Exception as exc:  # noqa: BLE001
        failures.append((label, instance, None, "EXC", repr(exc)))


# ----------------------------------------------------------------------
# Hand-picked edge cases
# ----------------------------------------------------------------------
check({"num_vars": 0, "clauses": []}, "empty m=0")
check({"num_vars": 5, "clauses": []}, "no clauses")
check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]}, "shared vars")
check({"num_vars": 4, "clauses": [[1, 2, 3], [2, 3, 4], [1, 3, 4]]}, "unsat-ish")
check({"num_vars": 10, "clauses": [[1, 2, 3]]}, "unused vars")
check({"num_vars": 3, "clauses": [[3, 1, 2]]}, "unordered clause")


# ----------------------------------------------------------------------
# Exhaustive small instances
# ----------------------------------------------------------------------
def all_clauses(m):
    return [list(c) for c in itertools.combinations(range(1, m + 1), 3)]


for m, max_k in [(3, 4), (4, 3), (5, 2), (6, 2)]:
    base_clauses = all_clauses(m)
    for k in range(0, max_k + 1):
        for combo in itertools.combinations_with_replacement(base_clauses, k):
            check({"num_vars": m, "clauses": [list(c) for c in combo]},
                  f"m={m} k={k}")

# ----------------------------------------------------------------------
# Random instances, including larger clause counts
# ----------------------------------------------------------------------
rng = random.Random(12345)
for trial in range(3000):
    m = rng.randint(3, 8)
    k = rng.randint(0, 8)
    clauses = [rng.sample(range(1, m + 1), 3) for _ in range(k)]
    check({"num_vars": m, "clauses": clauses}, f"random {trial}")

for trial in range(200):
    m = rng.randint(9, 13)
    k = rng.randint(0, 5)
    clauses = [rng.sample(range(1, m + 1), 3) for _ in range(k)]
    check({"num_vars": m, "clauses": clauses}, f"random-large {trial}")

# ----------------------------------------------------------------------
# Report + verdict
# ----------------------------------------------------------------------
print(f"tests_run={tests_run} tests_passed={tests_passed}")
if failures:
    print(f"FAILURES: {len(failures)}")
    for f in failures[:10]:
        print(f)
else:
    print("ALL TESTS PASSED")

verified = (len(failures) == 0 and tests_run > 0 and tests_passed == tests_run)
with open("verdict.json", "w") as fh:
    json.dump({"verified": verified,
               "tests_run": tests_run,
               "tests_passed": tests_passed}, fh)
print("verdict:", {"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed})
