import random

import problems
from problems import HamiltonianPath as SOURCE
from problems import Sat as TARGET
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
    assert got == expected, (instance, out, expected, got)
    tests_passed += 1


# Exhaustive over all graphs on 0..5 vertices.
for instance in SOURCE.enumerate_instances(5):
    check(instance)

# Random graphs on up to 8 vertices, various densities.
rng = random.Random(12345)
for _ in range(400):
    n = rng.randint(0, 8)
    p = rng.random()
    edges = [[u, v] for u in range(n) for v in range(u + 1, n) if rng.random() < p]
    check({"n": n, "edges": edges})

# A few structured cases: complete graphs, empty graphs, paths, cycles.
for n in range(0, 10):
    check({"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]})
    check({"n": n, "edges": []})
    check({"n": n, "edges": [[i, i + 1] for i in range(n - 1)]})
    if n >= 3:
        check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
