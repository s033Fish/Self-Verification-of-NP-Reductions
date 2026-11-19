import random

from problems import ThreeSat, VertexCover
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    out = reduce(instance)
    VertexCover.validate(out)          # reduction output must be well formed
    expected = ThreeSat.is_yes(instance)
    got = VertexCover.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        raise AssertionError(
            f"mismatch {label}: source={instance} expected={expected} "
            f"target={out} got={got}"
        )


# --- Explicit edge cases ---------------------------------------------------
check({"num_vars": 0, "clauses": []}, "empty m=0")
check({"num_vars": 1, "clauses": []}, "empty m=1")
check({"num_vars": 5, "clauses": []}, "empty m=5")
check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
check({"num_vars": 3, "clauses": [[-1, -2, -3]]}, "single negative clause")
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "contradiction")
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [-3, -4, 1]]}, "mixed")
# All 8 clauses over 3 vars: unsatisfiable.
check(
    {"num_vars": 3, "clauses": [
        [s1 * 1, s2 * 2, s3 * 3]
        for s1 in (1, -1) for s2 in (1, -1) for s3 in (1, -1)
    ]},
    "all 8 clauses",
)

# --- Exhaustive small instances -------------------------------------------
count = 0
for instance in ThreeSat.enumerate_instances(3):
    check(instance, "enumerate")
    count += 1
    if count >= 3000:
        break

# --- Random instances ------------------------------------------------------
rng = random.Random(12345)
for scale in range(0, 8):
    for _ in range(150):
        check(ThreeSat.random_instance(rng, scale), f"random scale={scale}")

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
