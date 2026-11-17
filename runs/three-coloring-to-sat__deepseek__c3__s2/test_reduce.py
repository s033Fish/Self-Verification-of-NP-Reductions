import itertools
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
    assert expected == got, (instance, out, expected, got)
    tests_passed += 1


# Exhaustive over all graphs with up to 6 vertices.
for n in range(0, 7):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        check({"n": n, "edges": edges})

# Random larger instances.
rng = random.Random(12345)
for _ in range(200):
    scale = rng.randint(0, 12)
    check(SOURCE.random_instance(rng, scale))

# Explicit edge cases.
check({"n": 0, "edges": []})
check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})  # K4 -> no
check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})  # K3 -> yes

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed

import json
with open("verdict.json", "w") as f:
    json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
