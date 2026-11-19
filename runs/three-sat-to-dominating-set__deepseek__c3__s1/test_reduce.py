import random
from itertools import combinations, product
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0
fails = []

def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    red = reduce(inst)
    TARGET.validate(red)
    a = SOURCE.is_yes(inst)
    b = TARGET.is_yes(red)
    if a == b:
        tests_passed += 1
    else:
        fails.append((inst, a, b))

# edge cases: no clauses, various m
for m in range(0, 6):
    check({"num_vars": m, "clauses": []})

# exhaustive formulas over m=3 (all clause subsets, distinct clauses)
m = 3
all_clauses = [
    [s * v for s, v in zip(signs, variables)]
    for variables in combinations(range(1, m + 1), 3)
    for signs in product((1, -1), repeat=3)
]
for mask in range(1 << len(all_clauses)):
    clauses = [c for i, c in enumerate(all_clauses) if mask >> i & 1]
    check({"num_vars": m, "clauses": clauses})

# small random formulas with few clauses (keeps brute force feasible)
rng = random.Random(12345)
def rand_small(m, maxc):
    clauses = []
    for _ in range(rng.randint(0, maxc)):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}

for m in range(3, 7):
    for _ in range(150):
        check(rand_small(m, 5))

# duplicates of clauses
for _ in range(200):
    inst = rand_small(rng.randint(3, 5), 4)
    if inst["clauses"]:
        inst["clauses"].append(list(inst["clauses"][0]))
    check(inst)

# known unsatisfiable formula (all 8 clauses over 3 vars)
check({"num_vars": 3, "clauses": [list(c) for c in all_clauses]})

print(f"tests_run={tests_run} tests_passed={tests_passed} fails={len(fails)}")
for f in fails[:5]:
    print("FAIL", f)
assert tests_run == tests_passed
