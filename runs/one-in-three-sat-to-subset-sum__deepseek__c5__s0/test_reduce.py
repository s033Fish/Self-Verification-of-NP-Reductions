"""Independent brute-force check of reduce.py for 1-in-3-SAT -> Subset Sum."""

from __future__ import annotations

import itertools
import random
import sys

from problems import OneInThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_one_in_three_sat(instance: dict) -> bool:
    """True iff some assignment makes exactly one var true in every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
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


def solve_subset_sum(instance: dict) -> bool:
    """True iff some sub-list (each position at most once) sums to target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures: list[str] = []


def check(instance: dict, label: str = "") -> None:
    global tests_run, tests_passed
    tests_run += 1
    try:
        OneInThreeSat.validate(instance)
    except Exception as exc:  # pragma: no cover
        failures.append(f"{label}: source instance invalid: {exc}")
        return
    expected = solve_one_in_three_sat(instance)
    reduced = reduce(instance)
    try:
        SubsetSum.validate(reduced)
    except Exception as exc:
        failures.append(f"{label}: reduced instance invalid: {exc} (got {reduced})")
        return
    got = solve_subset_sum(reduced)
    if got == expected:
        tests_passed += 1
    else:
        failures.append(
            f"{label}: mismatch source={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )


# ----------------------------------------------------------------------
# 1. Exhaustive small instances: all clause sets over m variables, small.

def all_clauses(m: int) -> list[list[int]]:
    return [list(c) for c in itertools.combinations(range(1, m + 1), 3)]


for m in range(0, 5):
    clauses_pool = all_clauses(m)
    # all subsets of the clause pool up to size 3 (with repetition allowed in
    # the problem, but subsets cover the structural cases)
    max_k = min(3, len(clauses_pool))
    for k in range(0, max_k + 1):
        for combo in itertools.combinations(clauses_pool, k):
            check({"num_vars": m, "clauses": [list(c) for c in combo]},
                  f"exhaustive m={m} k={k}")

# 2. Duplicate clauses and repeated variables across clauses.
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
      "all 4 clauses on 4 vars")
check({"num_vars": 5, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, "triple dup")
check({"num_vars": 6, "clauses": [[1, 2, 3], [3, 4, 5], [5, 6, 1], [2, 4, 6]]},
      "interlocking")

# 3. Edge cases.
check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
check({"num_vars": 1, "clauses": []}, "m=1 no clauses")
check({"num_vars": 7, "clauses": []}, "m=7 no clauses")

# 4. Random instances.
rng = random.Random(12345)
for _ in range(4000):
    m = rng.randint(0, 7)
    if m < 3:
        clauses = []
    else:
        n = rng.randint(0, 6)
        clauses = []
        for _ in range(n):
            clauses.append(rng.sample(range(1, m + 1), 3))
    check({"num_vars": m, "clauses": clauses}, "random")

# ----------------------------------------------------------------------
# 5. Polynomial-time / no-brute-force sanity: reduction on a moderately
#    large instance should complete quickly.
import time
big = {"num_vars": 40, "clauses": [list(rng.sample(range(1, 41), 3)) for _ in range(80)]}
t0 = time.time()
red_big = reduce(big)
dt = time.time() - t0
tests_run += 1
if dt < 5.0 and isinstance(red_big, dict) and "numbers" in red_big and "target" in red_big:
    tests_passed += 1
else:
    failures.append(f"large instance reduction too slow or malformed: {dt}s")

# ----------------------------------------------------------------------
print(f"tests_run={tests_run} tests_passed={tests_passed}")
if failures:
    print(f"FAILURES ({len(failures)}):")
    for f in failures[:20]:
        print("  " + f)
    sys.exit(1)
print("ALL TESTS PASSED")
