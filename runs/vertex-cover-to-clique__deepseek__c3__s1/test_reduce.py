import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce

# Exhaustive small instances: all graphs up to n=5, all relevant k.
tests_run = 0
tests_passed = 0

for n in range(0, 6):
    pairs = list(__import__("itertools").combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        for k in range(-2, n + 3):
            src = {"n": n, "edges": edges, "k": k}
            SOURCE.validate(src)
            out = reduce(src)
            TARGET.validate(out)
            expected = SOURCE.is_yes(src)
            got = TARGET.is_yes(out)
            tests_run += 1
            if expected == got:
                tests_passed += 1
            else:
                print("MISMATCH", src, out, expected, got)
                sys.exit(1)

# Random larger instances.
rng = random.Random(12345)
for _ in range(2000):
    n = rng.randint(0, 12)
    p = rng.random()
    edges = [
        [u, v]
        for u, v in __import__("itertools").combinations(range(n), 2)
        if rng.random() < p
    ]
    k = rng.randint(-3, n + 3)
    src = {"n": n, "edges": edges, "k": k}
    SOURCE.validate(src)
    out = reduce(src)
    TARGET.validate(out)
    expected = SOURCE.is_yes(src)
    got = TARGET.is_yes(out)
    tests_run += 1
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", src, out, expected, got)
        sys.exit(1)

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
