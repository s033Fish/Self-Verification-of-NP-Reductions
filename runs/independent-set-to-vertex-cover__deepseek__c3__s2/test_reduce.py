"""Tests for the Independent Set -> Vertex Cover reduction."""
import itertools
import random

import problems
from reduce import reduce

SOURCE = problems.SOURCE
TARGET = problems.TARGET


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if mask >> i & 1]


def brute_force_checks():
    tests = 0
    passed = 0
    # Exhaustive over all graphs with n = 0..5 and all k in -2..n+2.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                src = {"n": n, "edges": edges, "k": k}
                SOURCE.validate(src)
                tgt = reduce(src)
                TARGET.validate(tgt)
                tests += 1
                if SOURCE.is_yes(src) == TARGET.is_yes(tgt):
                    passed += 1
                else:
                    print("MISMATCH", src, tgt)
    return tests, passed


def random_checks(seed=12345, count=3000):
    rng = random.Random(seed)
    tests = 0
    passed = 0
    for _ in range(count):
        scale = rng.randint(0, 9)
        src = SOURCE.random_instance(rng, scale)
        SOURCE.validate(src)
        tgt = reduce(src)
        TARGET.validate(tgt)
        tests += 1
        if SOURCE.is_yes(src) == TARGET.is_yes(tgt):
            passed += 1
        else:
            print("MISMATCH", src, tgt)
    return tests, passed


if __name__ == "__main__":
    t1, p1 = brute_force_checks()
    t2, p2 = random_checks()
    tests = t1 + t2
    passed = p1 + p2
    print(f"brute-force: {p1}/{t1}, random: {p2}/{t2}")
    assert passed == tests, "some tests failed"
    print("ALL TESTS PASSED")
