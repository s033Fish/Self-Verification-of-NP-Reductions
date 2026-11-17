import itertools
import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print(f"FAIL {label}: instance={instance} expected={expected} got={got} out={out}")
        return False
    return True


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


ok = True

# Edge cases explicitly mentioned.
ok &= check({"n": 0, "edges": []}, "n=0")
ok &= check({"n": 1, "edges": []}, "n=1")
ok &= check({"n": 2, "edges": [[0, 1]]}, "n=2 edge")
ok &= check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "K3")
ok &= check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]]}, "K4")

# Exhaustive over all labelled graphs on 0..5 vertices.
for n in range(0, 6):
    for g in all_graphs(n):
        ok &= check(g, f"all n={n}")

# Random graphs on up to 9 vertices.
rng = random.Random(12345)
for _ in range(400):
    n = rng.randint(0, 9)
    pairs = list(itertools.combinations(range(n), 2))
    p = rng.random()
    edges = [list(e) for e in pairs if rng.random() < p]
    ok &= check({"n": n, "edges": edges}, "random")

print(f"tests_run={tests_run} tests_passed={tests_passed}")
sys.exit(0 if ok else 1)
