"""Tests for reduce.py: compare brute-force SAT and 3-SAT answers."""

from __future__ import annotations

import json
import random
import sys

import problems
from problems import Sat, ThreeSat
from reduce import reduce

tests_run = 0
tests_passed = 0
failures: list[str] = []


def check(instance, label):
    global tests_run, tests_passed
    tests_run += 1
    try:
        Sat.validate(instance)
        target = reduce(instance)
        ThreeSat.validate(target)
        expected = Sat.is_yes(instance)
        got = ThreeSat.is_yes(target)
        assert expected == got, f"{label}: SAT={expected} but 3-SAT={got}"
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{label}: {exc!r}")
        return
    tests_passed += 1


# 1. Exhaustive small SAT instances (num_vars <= 2).
for inst in Sat.enumerate_instances(2):
    check(inst, f"exhaustive:{json.dumps(inst, sort_keys=True)}")

# 2. Random instances over a range of scales.
rng = random.Random(12345)
for scale in range(0, 7):
    for _ in range(300):
        inst = Sat.random_instance(rng, scale)
        check(inst, f"random:{json.dumps(inst, sort_keys=True)}")

# 3. Hand-crafted edge cases.
edge_cases = [
    {"num_vars": 0, "clauses": []},
    {"num_vars": 0, "clauses": [[]]},
    {"num_vars": 3, "clauses": []},
    {"num_vars": 1, "clauses": [[1]]},
    {"num_vars": 1, "clauses": [[-1]]},
    {"num_vars": 1, "clauses": [[1], [-1]]},
    {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]},
    {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},
    {"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1, -2, -3, -4]]},
    {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},
    {"num_vars": 5, "clauses": [[1, 1, 1, 1]]},
    {"num_vars": 5, "clauses": [[1, -1, 2, 3, 4]]},  # tautology
    {"num_vars": 5, "clauses": [[1, 2], [1, 2], [-1, 2]]},
    {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6], [-1, -2, -3, -4, -5, -6]]},
    {"num_vars": 2, "clauses": [[1, 2, 1, -2]]},  # tautology via repeats
    {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2], [1], [-1, -2, -3]]},
]
for inst in edge_cases:
    check(inst, f"edge:{json.dumps(inst, sort_keys=True)}")

# 4. Random long-clause instances to exercise the chain construction.
rng2 = random.Random(999)
for _ in range(400):
    m = rng2.randint(3, 8)
    nclauses = rng2.randint(1, 6)
    clauses = []
    for _ in range(nclauses):
        length = rng2.randint(1, min(7, m))
        variables = rng2.sample(range(1, m + 1), length)
        clauses.append([v if rng2.random() < 0.5 else -v for v in variables])
    check({"num_vars": m, "clauses": clauses}, f"long:{json.dumps(clauses)}")

print(f"tests_run={tests_run} tests_passed={tests_passed}")
if failures:
    for f in failures[:20]:
        print("FAIL:", f)
    sys.exit(1)

verdict = {
    "verified": tests_run == tests_passed,
    "tests_run": tests_run,
    "tests_passed": tests_passed,
}
with open("verdict.json", "w") as fh:
    json.dump(verdict, fh)
print("verdict:", verdict)

# 5. Larger random instances (still brute-forceable) to stress chains.
rng3 = random.Random(2024)
for _ in range(200):
    m = rng3.randint(1, 10)
    clauses = []
    for _ in range(rng3.randint(1, 8)):
        length = rng3.randint(1, min(10, max(1, m)))
        variables = rng3.sample(range(1, m + 1), length) if m else []
        clauses.append([v if rng3.random() < 0.5 else -v for v in variables])
    check({"num_vars": m, "clauses": clauses}, f"larger:{json.dumps(clauses)}")

# 6. Polynomial-time sanity: a big instance reduces quickly.
import time
big = {"num_vars": 5000, "clauses": [[i if i % 2 else -i for i in range(1, 51)] for _ in range(500)]}
t0 = time.time()
out = reduce(big)
dt = time.time() - t0
ThreeSat.validate(out)
assert dt < 5.0, f"reduction too slow: {dt}s"
tests_run += 1
tests_passed += 1
print(f"big reduction: {dt:.3f}s, {len(out['clauses'])} clauses, {out['num_vars']} vars")

print(f"FINAL tests_run={tests_run} tests_passed={tests_passed}")
verdict = {"verified": tests_run == tests_passed, "tests_run": tests_run, "tests_passed": tests_passed}
with open("verdict.json", "w") as fh:
    json.dump(verdict, fh)
print("verdict:", verdict)
