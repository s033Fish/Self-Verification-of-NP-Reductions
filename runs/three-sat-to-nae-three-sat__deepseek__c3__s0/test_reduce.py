import random
import itertools
import problems
from problems import ThreeSat, NaeThreeSat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    out = reduce(instance)
    NaeThreeSat.validate(out)
    expected = ThreeSat.is_yes(instance)
    got = NaeThreeSat.is_yes(out)
    if expected == got:
        tests_passed += 1
        return True
    print("MISMATCH", instance, "expected", expected, "got", got, "reduced", out)
    return False


# 1. Exhaustive small formulas (num_vars <= 3, distinct clauses).
ok = True
for inst in ThreeSat.enumerate_instances(3):
    ok &= check(inst)

# 2. Random instances over a range of scales.
rng = random.Random(12345)
for scale in range(0, 9):
    for _ in range(200):
        inst = ThreeSat.random_instance(rng, scale)
        ok &= check(inst)

# 3. Hand-picked edge cases.
edge = [
    {"num_vars": 0, "clauses": []},
    {"num_vars": 1, "clauses": []},
    {"num_vars": 5, "clauses": []},
    {"num_vars": 3, "clauses": [[1, 2, 3]]},
    {"num_vars": 3, "clauses": [[-1, -2, -3]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3],
                                 [1, -2, -3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]},
    {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4],
                                 [-1, -2, -3], [-1, -2, -4], [-1, -3, -4], [-2, -3, -4]]},
]
for inst in edge:
    ok &= check(inst)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
print("ALL PASS" if ok and tests_run == tests_passed else "FAILURES")
