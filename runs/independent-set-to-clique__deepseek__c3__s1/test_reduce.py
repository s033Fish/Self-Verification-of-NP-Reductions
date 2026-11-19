import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(inst):
    global tests_run, tests_passed
    tests_run += 1
    out = reduce(inst)
    # The reduction must produce a valid target instance.
    TARGET.validate(out)
    expected = SOURCE.is_yes(inst)
    got = TARGET.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("FAIL", inst, "->", out, "expected", expected, "got", got)


# Exhaustive over all small graphs and a range of k values.
for n in range(0, 6):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        for k in range(-2, n + 3):
            check({"n": n, "edges": edges, "k": k})

# Random instances at a few scales.
rng = random.Random(12345)
for scale in range(1, 9):
    for _ in range(40):
        inst = SOURCE.random_instance(rng, scale)
        check(inst)

# Explicit edge cases.
check({"n": 0, "edges": [], "k": 0})
check({"n": 0, "edges": [], "k": 1})
check({"n": 5, "edges": [], "k": 5})
check({"n": 5, "edges": [], "k": 6})
check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3})
check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2})

print("tests_run", tests_run, "tests_passed", tests_passed)
assert tests_run == tests_passed
