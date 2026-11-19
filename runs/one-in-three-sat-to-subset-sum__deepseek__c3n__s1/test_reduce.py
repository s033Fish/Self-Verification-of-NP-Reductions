"""Tests: brute-force answers on small 1-in-3-SAT instances vs. their reductions."""

from __future__ import annotations

import itertools
import random

from problems import OneInThreeSat, SubsetSum
from reduce import reduce
from solvers import solve_one_in_three_sat, solve_subset_sum

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    OneInThreeSat.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    src = solve_one_in_three_sat(instance)
    tgt = solve_subset_sum(reduced)
    assert src == tgt, f"MISMATCH src={src} tgt={tgt}\n{instance}\n{reduced}"
    tests_passed += 1


# ---- exhaustive over all formulas with m variables and up to 2 clauses ----
def all_clauses(m):
    return [list(c) for c in itertools.combinations(range(1, m + 1), 3)]


for m in range(0, 6):
    cl = all_clauses(m)
    # no clauses
    check({"num_vars": m, "clauses": []})
    # single clause
    for c in cl:
        check({"num_vars": m, "clauses": [c]})
    # pairs of clauses (including duplicates)
    for c1 in cl:
        for c2 in cl:
            check({"num_vars": m, "clauses": [c1, c2]})

# ---- random larger-ish small instances ----
rng = random.Random(12345)
for _ in range(3000):
    m = rng.randint(3, 8)
    nclauses = rng.randint(0, 8)
    clauses = []
    for _ in range(nclauses):
        clauses.append(rng.sample(range(1, m + 1), 3))
    check({"num_vars": m, "clauses": clauses})

# ---- hand-picked edge cases ----
check({"num_vars": 0, "clauses": []})
check({"num_vars": 3, "clauses": [[1, 2, 3]]})
# (x1 or x2 or x3) & (x1 or x2 or x3) duplicated
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
# unsat: forces x1 and x2 both true in clause1 but exactly one in clause2
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
# variable not appearing anywhere
check({"num_vars": 5, "clauses": [[1, 2, 3]]})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
