import random
import problems
from problems import ThreeColoring, IndependentSet
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    out = reduce(inst)
    IndependentSet.validate(out)
    expected = ThreeColoring.is_yes(inst)
    got = IndependentSet.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", inst, "->", out, "expected", expected, "got", got)


# Exhaustive small graphs.
for scale in range(5):
    for inst in ThreeColoring.enumerate_instances(scale):
        check(inst)

# Random larger graphs.
rng = random.Random(12345)
for _ in range(2000):
    scale = rng.randint(0, 8)
    inst = ThreeColoring.random_instance(rng, scale)
    check(inst)

# Explicit edge cases.
check({"n": 0, "edges": []})
check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})

print("tests_run", tests_run, "tests_passed", tests_passed)
assert tests_run == tests_passed

import json
with open("verdict.json", "w") as f:
    json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
