"""Tests for the 3-Coloring -> 3-SAT reduction in reduce.py.

Compares problems.ThreeColoring.is_yes on a source instance with
problems.ThreeSat.is_yes on reduce(instance), over many small instances.
Also validates that every produced instance is a legal 3-SAT instance.
"""

import itertools
import random
import sys

from problems import ThreeColoring, ThreeSat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeColoring.validate(instance)
    target = reduce(instance)
    ThreeSat.validate(target)  # must be a legal 3-SAT instance
    expected = ThreeColoring.is_yes(instance)
    got = ThreeSat.is_yes(target)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "expected", expected, "got", got, file=sys.stderr)
        print("target:", target, file=sys.stderr)


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield {
            "n": n,
            "edges": [list(pair) for i, pair in enumerate(pairs) if mask >> i & 1],
        }


def main():
    # Exhaustive over all labelled graphs for n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Exhaustive n = 6 (32768 graphs) -- still fast enough.
    for g in all_graphs(6):
        check(g)

    # Random larger instances, including sparse/dense and structured graphs.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 12)
        p = rng.random()
        edges = [
            [u, v]
            for u, v in itertools.combinations(range(n), 2)
            if rng.random() < p
        ]
        check({"n": n, "edges": edges})

    # K4 and K5 must be no; small graphs must be yes.
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})
    check({"n": 5, "edges": [[u, v] for u, v in itertools.combinations(range(5), 2)]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    check({"n": 0, "edges": []})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    return 0


if __name__ == "__main__":
    sys.exit(main())
