import itertools
import random

from problems import Sat, IndependentSet
from reduce import reduce
from solvers import sat_solve, is_solve

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    Sat.validate(instance)
    out = reduce(instance)
    IndependentSet.validate(out)
    expected = sat_solve(instance)
    got = is_solve(out)
    assert got == expected, (instance, out, expected, got)
    tests_passed += 1


# --- hand-crafted edge cases ---
check({"num_vars": 0, "clauses": []})                     # yes
check({"num_vars": 0, "clauses": [[]]})                   # no (empty clause)
check({"num_vars": 1, "clauses": [[1]]})                  # yes
check({"num_vars": 1, "clauses": [[-1]]})                 # yes
check({"num_vars": 1, "clauses": [[1], [-1]]})            # no
check({"num_vars": 2, "clauses": [[1, 2], [-1], [-2]]})   # no
check({"num_vars": 2, "clauses": [[1, 2]]})               # yes
check({"num_vars": 3, "clauses": [[1, 1, 1]]})            # yes
check({"num_vars": 3, "clauses": [[1, -1]]})              # yes
check({"num_vars": 3, "clauses": [[1], [1], [1]]})        # yes
check({"num_vars": 2, "clauses": [[1, 2], [1, -2], [-1, 2], [-1, -2]]})  # no

# --- exhaustive small random formulas ---
rng = random.Random(12345)
for _ in range(4000):
    m = rng.randint(0, 4)
    nclauses = rng.randint(0, 5)
    clauses = []
    for _ in range(nclauses):
        clen = rng.randint(0, 3) if m > 0 else 0
        clause = []
        for _ in range(clen):
            v = rng.randint(1, m)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    check({"num_vars": m, "clauses": clauses})

# --- exhaustive over all formulas with m<=2, up to 3 clauses of size<=2 ---
def all_clauses(m):
    lits = [l for v in range(1, m + 1) for l in (v, -v)]
    res = [[]]
    for l in lits:
        res.append([l])
    for a, b in itertools.combinations(lits, 2):
        res.append([a, b])
    return res

for m in range(0, 3):
    pool = all_clauses(m)
    for nclauses in range(0, 4):
        for combo in itertools.combinations_with_replacement(pool, nclauses):
            check({"num_vars": m, "clauses": [list(c) for c in combo]})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
