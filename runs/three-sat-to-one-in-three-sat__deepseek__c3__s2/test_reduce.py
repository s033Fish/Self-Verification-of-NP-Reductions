import random

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0

def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "expected", expected, "got", got, "reduced", reduced)

# 1. Exhaustive over all small formulas (num_vars <= 3, distinct clauses).
for instance in SOURCE.enumerate_instances(3):
    check(instance)

# 2. Random instances at several scales (small enough for brute force).
rng = random.Random(12345)
for scale in range(0, 8):
    for _ in range(60):
        check(SOURCE.random_instance(rng, scale))

# 3. Larger random instances.
rng2 = random.Random(999)
for scale in range(8, 12):
    for _ in range(30):
        check(SOURCE.random_instance(rng2, scale))

# 4. Edge cases.
check({"num_vars": 0, "clauses": []})
check({"num_vars": 5, "clauses": []})
check({"num_vars": 3, "clauses": [[1, 2, 3]]})
check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3]]})
check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4],
                                  [-1, -2, -3], [-1, -2, -4], [-1, -3, -4], [-2, -3, -4]]})

# 5. Structural checks: reduction is polynomial (linear) in input size.
for scale in (10, 50, 100, 200):
    inst = {"num_vars": scale, "clauses": [[1, 2, 3]] * scale}
    red = reduce(inst)
    tests_run += 1
    if red["num_vars"] <= 6 * scale + 10 and len(red["clauses"]) <= 4 * scale + 10:
        tests_passed += 1
    else:
        print("SIZE BLOWUP", scale, red["num_vars"], len(red["clauses"]))

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"
