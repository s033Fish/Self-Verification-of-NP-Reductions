"""Tests comparing brute-force solvers on Clique instances and reductions."""

import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    reduced = reduce(instance)
    SOURCE.validate(instance)
    TARGET.validate(reduced)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(reduced)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "->", reduced, "expected", expected, "got", got)
        raise AssertionError("reduction mismatch")


def main():
    # Exhaustive small graphs with many k values.
    for n in range(0, 6):
        pairs = list(__import__("itertools").combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random instances at a few scales.
    rng = random.Random(12345)
    for scale in range(0, 9):
        for _ in range(200):
            inst = SOURCE.random_instance(rng, scale)
            check(inst)

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 2})
    check({"n": 5, "edges": [], "k": 5})
    check({"n": 5, "edges": [], "k": 6})
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]], "k": 3})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return 0


if __name__ == "__main__":
    sys.exit(main())
