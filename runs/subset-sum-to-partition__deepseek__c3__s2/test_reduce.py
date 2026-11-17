import random
import problems
from problems import SubsetSum, Partition
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    red = reduce(inst)
    Partition.validate(red)
    expected = SubsetSum.is_yes(inst)
    got = Partition.is_yes(red)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", inst, "->", red, "expected", expected, "got", got)


# Exhaustive small instances (values 0..3, all targets in range).
for scale in range(0, 5):
    for inst in SubsetSum.enumerate_instances(scale):
        check(inst)

# Explicit edge cases.
edge = [
    {"numbers": [], "target": 0},
    {"numbers": [], "target": 1},
    {"numbers": [], "target": -5},
    {"numbers": [0, 0, 0], "target": 0},
    {"numbers": [5], "target": 5},
    {"numbers": [5], "target": 4},
    {"numbers": [5], "target": 0},
    {"numbers": [1, 2, 3], "target": 3},
    {"numbers": [1, 2, 3], "target": 6},
    {"numbers": [1, 2, 3], "target": 7},
    {"numbers": [1, 2, 3], "target": 100},
    {"numbers": [4, 4, 4], "target": 8},
    {"numbers": [4, 4, 4], "target": 4},
    {"numbers": [4, 4, 4], "target": 12},
    {"numbers": [10, 0, 0, 3], "target": 3},
    {"numbers": [10**18, 1], "target": 10**18},
    {"numbers": [10**18, 1], "target": 10**18 + 1},
    {"numbers": [10**18, 1], "target": 1},
]
for inst in edge:
    check(inst)

# Random tests.
rng = random.Random(12345)
for scale in range(0, 13):
    for _ in range(400):
        check(SubsetSum.random_instance(rng, scale))

# Random tests with larger values.
for _ in range(2000):
    n = rng.randint(0, 8)
    nums = [rng.randint(0, 40) for _ in range(n)]
    t = rng.randint(-3, sum(nums) + 5)
    check({"numbers": nums, "target": t})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"
