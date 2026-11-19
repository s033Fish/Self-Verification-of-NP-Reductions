import random
import problems
from problems import HamiltonianCycle, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    HamiltonianCycle.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = HamiltonianCycle.is_yes(instance)
    got = Sat.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "expected", expected, "got", got)
        print("reduction", out)


# Exhaustive over all graphs with n = 0..6.
for scale in range(0, 6):
    for instance in HamiltonianCycle.enumerate_instances(scale):
        check(instance)

# Random larger instances.
rng = random.Random(12345)
for scale in range(3, 13):
    for _ in range(40):
        instance = HamiltonianCycle.random_instance(rng, scale)
        check(instance)

# Structured: cycles, paths, complete graphs, empty graphs.
for n in range(0, 12):
    check({"n": n, "edges": []})
    check({"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]})
    if n >= 3:
        check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})
        check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n - 1)]})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed

import json
with open("verdict.json", "w") as f:
    json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
