import random
import sys

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
    assert expected == got, (instance, out, expected, got)
    tests_passed += 1


# Exhaustive small enumeration.
for scale in range(0, 3):
    for inst in SOURCE.enumerate_instances(scale):
        check(inst)

# Random instances across scales.
rng = random.Random(12345)
for scale in range(0, 9):
    for _ in range(300):
        check(SOURCE.random_instance(rng, scale))

# Hand-picked edge cases.
edge_cases = [
    {"num_vars": 0, "clauses": []},
    {"num_vars": 0, "clauses": [[]]},
    {"num_vars": 1, "clauses": []},
    {"num_vars": 1, "clauses": [[]]},
    {"num_vars": 1, "clauses": [[1]]},
    {"num_vars": 1, "clauses": [[-1]]},
    {"num_vars": 1, "clauses": [[1], [-1]]},
    {"num_vars": 2, "clauses": [[1, 2], [-1], [-2]]},
    {"num_vars": 2, "clauses": [[1, 1], [-1, -1]]},
    {"num_vars": 2, "clauses": [[1, -1]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2], [-3]]},
    {"num_vars": 3, "clauses": [[1, -1], [2, -2], [3, -3]]},
    {"num_vars": 3, "clauses": [[1], [1], [1]]},
]
for inst in edge_cases:
    check(inst)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
