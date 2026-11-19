import random
import problems
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "expected", expected, "got", got, "out", out)
        raise AssertionError("mismatch")


# Exhaustive enumeration of small formulas (scale up to 3 variables).
for scale in range(0, 6):
    for instance in SOURCE.enumerate_instances(scale):
        check(instance)
print("exhaustive small done", tests_run, tests_passed)

# Random instances of various sizes.
rng = random.Random(12345)
for trial in range(3000):
    scale = rng.randint(0, 9)
    instance = SOURCE.random_instance(rng, scale)
    check(instance)
print("random done", tests_run, tests_passed)

# Edge cases.
check({"num_vars": 0, "clauses": []})
check({"num_vars": 5, "clauses": []})
check({"num_vars": 3, "clauses": [[1, 2, 3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]})
check({"num_vars": 6, "clauses": [[1, 2, 3], [4, 5, 6], [1, 4, 5]]})

print("ALL DONE", tests_run, tests_passed)
