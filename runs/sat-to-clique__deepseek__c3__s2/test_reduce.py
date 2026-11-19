import random
import problems
from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    red = reduce(inst)
    # reduction output must be a valid Clique instance
    TARGET.validate(red)
    got = TARGET.is_yes(red)
    want = SOURCE.is_yes(inst)
    if got == want:
        tests_passed += 1
    else:
        print("MISMATCH", inst, "->", red, "want", want, "got", got)
    return got == want


# 1. Exhaustive enumeration of small formulas.
count = 0
for inst in SOURCE.enumerate_instances(2):
    check(inst)
    count += 1
print("enumerated", count, "formulas up to 3 vars")

# 2. Random instances across scales.
rng = random.Random(12345)
for scale in range(0, 6):
    for _ in range(150):
        check(SOURCE.random_instance(rng, scale))
print("random done")

# 3. Hand-picked edge cases.
edge_cases = [
    {"num_vars": 0, "clauses": []},
    {"num_vars": 0, "clauses": [[]]},
    {"num_vars": 1, "clauses": [[]]},
    {"num_vars": 3, "clauses": []},
    {"num_vars": 3, "clauses": [[1], [-1]]},
    {"num_vars": 3, "clauses": [[1, -1]]},
    {"num_vars": 3, "clauses": [[1, 1, 1]]},
    {"num_vars": 3, "clauses": [[1], [1], [1]]},
    {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]},
    {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2], []]},
    {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2], [3, -4], [4]]},
    {"num_vars": 5, "clauses": [[-1], [-2], [-3], [-4], [-5]]},
    {"num_vars": 5, "clauses": [[1, 2], [2, 3], [-2, 4], [-4, 5], [-5, -1]]},
]
for inst in edge_cases:
    check(inst)
print("edge cases done")

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"
