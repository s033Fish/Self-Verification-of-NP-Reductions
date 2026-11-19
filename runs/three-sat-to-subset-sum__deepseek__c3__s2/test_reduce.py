"""Test the 3-SAT -> Subset Sum reduction against the brute-force solvers."""
import random
import json

from problems import ThreeSat, SubsetSum
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)  # must be a legal Subset Sum instance
    expected = ThreeSat.is_yes(instance)
    got = SubsetSum.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH")
        print("  source:", instance)
        print("  expected:", expected, "got:", got)
        print("  reduced:", reduced)


# 1. Exhaustive: every 3-SAT instance with num_vars <= 3 (distinct clauses).
count = 0
for instance in ThreeSat.enumerate_instances(3):
    check(instance)
    count += 1
print("enumerated instances:", count)

# 2. Random small instances across several scales.
rng = random.Random(12345)
for scale in range(0, 6):
    for _ in range(300):
        check(ThreeSat.random_instance(rng, scale))

# 3. Hand-picked edge cases.
edge = [
    {"num_vars": 0, "clauses": []},
    {"num_vars": 1, "clauses": []},
    {"num_vars": 5, "clauses": []},
    {"num_vars": 3, "clauses": [[1, 2, 3]]},
    {"num_vars": 3, "clauses": [[-1, -2, -3]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
    {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
    {"num_vars": 3, "clauses": [[1, -2, 3], [-1, 2, -3], [1, 2, -3], [-1, -2, 3]]},
    {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [4, -1, 2]]},
    {"num_vars": 6, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 5, 6], [-4, -5, -6],
                                [1, 4, -2], [-3, 5, -6]]},
    {"num_vars": 8, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 5, 6], [-4, -5, -6],
                                [7, 8, 1], [-7, -8, -1]]},
]
for instance in edge:
    check(instance)

# 4. Larger random instances with few clauses (brute-forceable).
for scale in range(6, 12):
    for _ in range(5):
        nclauses = rng.randint(0, 4)
        clauses = []
        for _ in range(nclauses):
            vs = rng.sample(range(1, scale + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        check({"num_vars": scale, "clauses": clauses})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"

with open("verdict.json", "w") as f:
    json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
print("verdict written")
