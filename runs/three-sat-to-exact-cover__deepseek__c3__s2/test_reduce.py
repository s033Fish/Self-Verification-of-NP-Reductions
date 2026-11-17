import random

import problems
from problems import ThreeSat, ExactCover
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    reduced = reduce(instance)
    ExactCover.validate(reduced)  # reduction must emit valid target instances
    expected = ThreeSat.is_yes(instance)
    got = ExactCover.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH")
        print("source:", instance)
        print("expected:", expected, "got:", got)
        print("target:", reduced)


# 1. Exhaustive: every formula with num_vars <= 3 (distinct clauses).
for inst in ThreeSat.enumerate_instances(3):
    check(inst)

# 2. Random formulas across several scales.
rng = random.Random(12345)
for scale in range(0, 7):
    for _ in range(400):
        check(ThreeSat.random_instance(rng, scale))

# 3. Edge cases.
check({"num_vars": 0, "clauses": []})
check({"num_vars": 5, "clauses": []})
check({"num_vars": 3, "clauses": [[1, 2, 3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [1, 2, -3], [-1, -2, 3]]})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"

# 4. Larger random formulas.
rng2 = random.Random(999)
for scale in range(7, 13):
    for _ in range(60):
        check(ThreeSat.random_instance(rng2, scale))

# 5. Reduction size is polynomial.
for scale in range(0, 30):
    inst = ThreeSat.random_instance(random.Random(scale), scale)
    red = reduce(inst)
    n = len(inst["clauses"])
    assert red["universe_size"] == inst["num_vars"] + 4 * n
    assert len(red["sets"]) == 2 * inst["num_vars"] + 6 * n

print(f"FINAL tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
