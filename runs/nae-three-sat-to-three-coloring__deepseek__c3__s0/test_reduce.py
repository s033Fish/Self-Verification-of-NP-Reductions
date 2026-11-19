import random

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    NaeThreeSat.validate(instance)
    out = reduce(instance)
    ThreeColoring.validate(out)
    expected = NaeThreeSat.is_yes(instance)
    got = ThreeColoring.is_yes(out)
    assert got == expected, (
        f"mismatch for {instance}: source={expected} target={got} reduced={out}"
    )
    tests_passed += 1


# 1. Exhaustive over all formulas with num_vars <= 3 (distinct clauses).
for inst in NaeThreeSat.enumerate_instances(3):
    check(inst)

# 2. Random formulas across small scales (brute force stays fast).
rng = random.Random(12345)
for scale in range(0, 6):
    for _ in range(15):
        check(NaeThreeSat.random_instance(rng, scale))

# 3. Explicit edge cases.
check({"num_vars": 0, "clauses": []})
check({"num_vars": 1, "clauses": []})
check({"num_vars": 2, "clauses": []})
check({"num_vars": 5, "clauses": []})
# Duplicate clauses.
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]})
# A single clause is always NAE-satisfiable.
check({"num_vars": 3, "clauses": [[1, 2, 3]]})
check({"num_vars": 3, "clauses": [[1, -2, 3]]})
# Unused variables.
check({"num_vars": 6, "clauses": [[1, 2, 3]]})
# A few hand-built formulas, including unsatisfiable ones.
check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]})
check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
