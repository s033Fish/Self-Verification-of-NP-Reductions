"""Compare the brute-force solvers on small Partition instances and reductions."""
import random

from problems import Partition, SubsetSum
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    reduced = reduce(instance)
    # The reduction must produce a valid Subset Sum instance.
    SubsetSum.validate(reduced)
    expected = Partition.is_yes(instance)
    got = SubsetSum.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "->", reduced, "expected", expected, "got", got)


# Exhaustive small instances (numbers drawn from 0..3).
for scale in range(0, 7):
    for instance in Partition.enumerate_instances(scale):
        check(instance)

# Random instances, including larger values and many zeros.
rng = random.Random(12345)
for scale in range(0, 13):
    for _ in range(200):
        check(Partition.random_instance(rng, scale))

# Hand-picked edge cases.
for instance in [
    {"numbers": []},                 # empty: yes
    {"numbers": [0]},                # yes
    {"numbers": [1]},                # odd total: no
    {"numbers": [1, 2]},             # odd total: no
    {"numbers": [2, 2]},             # yes
    {"numbers": [0, 0, 0]},          # yes
    {"numbers": [5, 1, 2, 2]},       # yes (5 = 1+2+2)
    {"numbers": [10**30, 10**30]},   # huge: yes
    {"numbers": [10**30, 1]},        # huge odd: no
    {"numbers": [3, 3, 3]},          # odd total: no
]:
    check(instance)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"

# Larger random instances, sometimes padded with zeros.
rng2 = random.Random(999)
for scale in range(0, 21):
    for _ in range(100):
        inst = Partition.random_instance(rng2, scale)
        if rng2.random() < 0.5:
            inst = {"numbers": inst["numbers"] + [0] * rng2.randint(0, 4)}
        check(inst)

print(f"final tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"
