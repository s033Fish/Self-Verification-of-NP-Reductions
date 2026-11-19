"""Tests for reduce.py: compare VertexCover and Sat brute-force solvers."""
import random

from problems import VertexCover, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    VertexCover.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = VertexCover.is_yes(instance)
    got = Sat.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print(f"MISMATCH source={instance} expected={expected} got={got}")
        print(f"  reduced={reduced}")
    return expected == got


# 1. Exhaustive small graphs with every k from -1 to n+1.
for instance in VertexCover.enumerate_instances(4):
    check(instance)

# 2. Random instances over a range of scales, including larger ones.
rng = random.Random(12345)
for scale in range(0, 9):
    for _ in range(300):
        check(VertexCover.random_instance(rng, scale))

# 3. Targeted edge cases.
edge_cases = [
    {"n": 0, "edges": [], "k": -5},
    {"n": 0, "edges": [], "k": 0},
    {"n": 0, "edges": [], "k": 3},
    {"n": 1, "edges": [], "k": 0},
    {"n": 1, "edges": [], "k": 1},
    {"n": 5, "edges": [], "k": 0},
    {"n": 5, "edges": [], "k": 2},
    {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
    {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
    {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 1},
    {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 0},
    {"n": 6, "edges": [[i, j] for i in range(6) for j in range(i + 1, 6)], "k": 5},
    {"n": 6, "edges": [[i, j] for i in range(6) for j in range(i + 1, 6)], "k": 6},
    {"n": 3, "edges": [[0, 1], [1, 2]], "k": -1},
    {"n": 3, "edges": [[0, 1], [1, 2]], "k": 100},
]
for instance in edge_cases:
    check(instance)

# 4. Larger random instances to exercise the sequential counter beyond k=1.
for scale in range(10, 16):
    for _ in range(60):
        check(VertexCover.random_instance(rng, scale))

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed, "some tests failed"

import json
with open("verdict.json", "w") as f:
    json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
print("verdict.json written")
