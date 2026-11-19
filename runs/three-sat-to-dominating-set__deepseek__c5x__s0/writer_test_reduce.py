import itertools
import random

import problems
from problems import ThreeSat, DominatingSet
from solvers import sat_solve, ds_solve
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(inst)
    out = reduce(inst)
    DominatingSet.validate(out)
    a = sat_solve(inst)
    b = ds_solve(out)
    if a != b:
        raise AssertionError(
            f"MISMATCH src={inst} src_ans={a} out={out} out_ans={b}"
        )
    tests_passed += 1


def all_clauses(m):
    """All valid 3-literal clauses over variables 1..m."""
    clauses = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, vars_)])
    return clauses


# --- exhaustive: m = 3, every subset of all 8 possible clauses -------------
cl3 = all_clauses(3)
for r in range(len(cl3) + 1):
    for sub in itertools.combinations(cl3, r):
        check({"num_vars": 3, "clauses": [list(c) for c in sub]})

# --- edge cases: no clauses, m = 0..5 -------------------------------------
for m in range(0, 6):
    check({"num_vars": m, "clauses": []})

# --- exhaustive: m = 4, all subsets of a fixed small clause pool -----------
cl4 = all_clauses(4)
for r in range(0, 4):
    for sub in itertools.combinations(cl4, r):
        check({"num_vars": 4, "clauses": [list(c) for c in sub]})

# --- randomized tests ------------------------------------------------------
rng = random.Random(12345)
for _ in range(3000):
    m = rng.randint(3, 7)
    pool = all_clauses(m)
    c = rng.randint(0, 8)
    clauses = [list(rng.choice(pool)) for _ in range(c)]
    # duplicate clauses allowed; literal order shuffled
    for cl in clauses:
        rng.shuffle(cl)
    rng.shuffle(clauses)
    check({"num_vars": m, "clauses": clauses})

# --- randomized with unused variables and duplicates -----------------------
for _ in range(1000):
    m = rng.randint(3, 6)
    pool = all_clauses(m)
    clauses = [list(rng.choice(pool)) for _ in range(rng.randint(0, 6))]
    check({"num_vars": m, "clauses": clauses})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
