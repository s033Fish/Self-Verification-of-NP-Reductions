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
    assert got == expected, (
        f"mismatch: source={instance!r} -> target={out!r}, "
        f"expected {expected}, got {got}"
    )
    tests_passed += 1


# Explicit edge cases.
check({"num_vars": 0, "clauses": []})
check({"num_vars": 5, "clauses": []})
check({"num_vars": 3, "clauses": [[1, 2, 3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3],
                                  [-1, 2, -3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})

# Exhaustive over all distinct-clause formulas with num_vars <= 3.
for instance in SOURCE.enumerate_instances(3):
    check(instance)

# Random formulas across a range of sizes.
rng = random.Random(12345)
for scale in range(0, 6):
    for _ in range(30):
        check(SOURCE.random_instance(rng, scale))

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
