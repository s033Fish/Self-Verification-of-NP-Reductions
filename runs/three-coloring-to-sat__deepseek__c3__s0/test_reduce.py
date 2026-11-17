"""Tests comparing brute-force 3-Coloring with SAT on reduced instances."""
import random

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    assert got == expected, (
        f"mismatch on {instance}: source={expected} target={got} reduced={reduced}"
    )
    tests_passed += 1


# Exhaustive: every graph on 0..5 vertices (1 + 1 + 2 + 8 + 64 + 1024 = 1100).
for scale in range(0, 6):
    for instance in SOURCE.enumerate_instances(scale):
        check(instance)

# Random graphs of various sizes and densities.
rng = random.Random(12345)
for _ in range(400):
    n = rng.randint(0, 9)
    p = rng.random()
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    check({"n": n, "edges": edges})

# Random instances via the problem's own generator.
for scale in range(0, 10):
    for _ in range(30):
        check(SOURCE.random_instance(rng, scale))

# Explicit edge cases.
check({"n": 0, "edges": []})
check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})  # K4 -> no
check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]})  # K5 -> no

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
