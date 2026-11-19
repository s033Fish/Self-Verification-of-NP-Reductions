import itertools
import random

from problems import ThreeSat, IndependentSet
from reduce import reduce
from solvers import solve_three_sat, solve_independent_set

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    out = reduce(instance)
    IndependentSet.validate(out)
    src = solve_three_sat(instance)
    tgt = solve_independent_set(out)
    if src == tgt:
        tests_passed += 1
    else:
        print("FAIL", label, instance, "->", out, "src", src, "tgt", tgt)
        raise AssertionError("mismatch")


# --- explicit edge cases -------------------------------------------------
check({"num_vars": 0, "clauses": []}, "empty m=0")
check({"num_vars": 1, "clauses": []}, "empty m=1")
check({"num_vars": 5, "clauses": []}, "empty m=5")

# unsat: all 8 clauses over 3 vars
all_clauses = [list(c) for c in itertools.product([1, -1, 2, -2, 3, -3], repeat=3)
               if len({abs(x) for x in c}) == 3]
# dedupe sign patterns
seen = set()
uniq = []
for c in all_clauses:
    key = tuple(sorted(c))
    if key not in seen:
        seen.add(key)
        uniq.append(list(c))
check({"num_vars": 3, "clauses": uniq}, "all 3-var clauses (unsat)")
check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single sat")
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "two clauses")
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
                                  [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3]]},
      "full unsat explicit")

# --- exhaustive small random-ish enumeration ----------------------------
rng = random.Random(12345)


def random_instance(m, num_clauses):
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


for m in range(0, 6):
    for nc in range(0, 7):
        if nc > 0 and m < 3:
            continue
        for _ in range(30):
            check(random_instance(m, nc), f"random m={m} nc={nc}")

# exhaustive over all clauses for m=3 with up to 2 clauses
base_clauses = []
for c in itertools.product([1, -1, 2, -2, 3, -3], repeat=3):
    if len({abs(x) for x in c}) == 3:
        base_clauses.append(list(c))
for c1 in base_clauses:
    check({"num_vars": 3, "clauses": [c1]}, "exh1")
    for c2 in base_clauses:
        check({"num_vars": 3, "clauses": [c1, c2]}, "exh2")

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
