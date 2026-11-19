import random

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(inst)
    out = reduce(inst)
    TARGET.validate(out)
    expected = SOURCE.is_yes(inst)
    got = TARGET.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH")
        print("  source:", inst)
        print("  expected:", expected, "got:", got)
        print("  target:", out)
        raise SystemExit(1)


# 1) Exhaustive small 3-SAT instances (all formulas up to 3 variables).
for inst in SOURCE.enumerate_instances(3):
    check(inst)

# 2) Random instances across small scales (keep graphs small for brute force).
rng = random.Random(12345)
for scale in range(0, 5):
    for _ in range(40):
        check(SOURCE.random_instance(rng, scale))

# 3) Random instances with a bounded number of clauses for larger scales.
for scale in range(5, 10):
    for _ in range(25):
        clauses = []
        for _ in range(rng.randint(0, 12)):
            variables = rng.sample(range(1, scale + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in sorted(variables)])
        check({"num_vars": scale, "clauses": clauses})

# 4) More random seeds at small scales.
for seed in range(10):
    r2 = random.Random(seed)
    for scale in range(0, 4):
        for _ in range(10):
            check(SOURCE.random_instance(r2, scale))

# 5) Explicit edge cases.
check({"num_vars": 0, "clauses": []})
check({"num_vars": 1, "clauses": []})
check({"num_vars": 5, "clauses": []})
check({"num_vars": 3, "clauses": [[1, 2, 3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
check({"num_vars": 3, "clauses": [[1, -2, 3], [1, -2, 3]]})  # duplicate clause
check({"num_vars": 3, "clauses": [
    [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
    [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
]})  # unsatisfiable
# previously failing instance (single-vertex gadget bug)
check({'num_vars': 4, 'clauses': [[-1,-3,4],[1,2,4],[1,-3,4],[2,-3,-4],[-1,-2,3],
    [-1,-3,4],[1,3,4],[-1,2,3],[-1,-2,-4],[-1,3,-4],[-2,-3,4],[1,-3,-4],[1,3,-4],
    [-2,-3,-4],[-1,2,-3],[1,-3,4],[1,3,-4],[2,-3,4],[2,3,-4],[1,-2,3],[2,3,4],
    [2,-3,4],[-1,-3,4],[1,-3,4],[1,2,-3],[-1,3,4],[1,-2,-3],[-1,2,-3],[-2,-3,4],
    [1,3,4],[-2,3,4]]})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
