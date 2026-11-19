import random
import sys

from problems import ExactCover, SubsetSum
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ExactCover.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    expected = ExactCover.is_yes(instance)
    got = SubsetSum.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH")
        print("  source  :", instance)
        print("  reduced :", reduced)
        print("  expected:", expected, "got:", got)
        sys.exit(1)


# 1. Exhaustive small instances via enumerate_instances.
for scale in range(0, 4):
    count = 0
    for instance in ExactCover.enumerate_instances(scale):
        check(instance)
        count += 1
    print(f"exhaustive scale {scale}: {count} instances")

# 2. Hand-crafted edge cases.
edge_cases = [
    {"universe_size": 0, "sets": []},
    {"universe_size": 0, "sets": [[], []]},
    {"universe_size": 1, "sets": []},
    {"universe_size": 1, "sets": [[0]]},
    {"universe_size": 1, "sets": [[0], [0]]},
    {"universe_size": 2, "sets": [[0, 1], [0], [1]]},
    {"universe_size": 2, "sets": [[0], [1], [0, 1]]},
    {"universe_size": 2, "sets": [[0, 1], [0, 1]]},
    {"universe_size": 3, "sets": [[], [0], [1], [2], [0, 1], [2]]},
    {"universe_size": 3, "sets": [[0, 1, 2]]},
    {"universe_size": 3, "sets": [[0, 1], [2]]},
    {"universe_size": 4, "sets": [[0, 1], [2, 3], [0, 2], [1, 3]]},
    {"universe_size": 4, "sets": [[0, 1, 2, 3], [0], [1], [2], [3]]},
    {"universe_size": 5, "sets": []},
    {"universe_size": 5, "sets": [[0], [1], [2], [3], [4]]},
    {"universe_size": 5, "sets": [[0, 1, 2, 3, 4], [0, 1, 2, 3, 4]]},
]
for instance in edge_cases:
    check(instance)
print("edge cases done")

# 3. Random instances at several scales.
rng = random.Random(12345)
for scale in range(0, 9):
    for _ in range(300):
        instance = ExactCover.random_instance(rng, scale)
        check(instance)
print("random instances done")

# 4. Random instances with deliberately duplicated/empty sets.
for _ in range(500):
    u = rng.randint(0, 7)
    sets = []
    for _ in range(rng.randint(0, 10)):
        s = [e for e in range(u) if rng.random() < 0.5]
        sets.append(s)
        if s and rng.random() < 0.3:
            sets.append(list(s))  # duplicate
    instance = {"universe_size": u, "sets": sets}
    check(instance)
print("duplicate/empty instances done")

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
