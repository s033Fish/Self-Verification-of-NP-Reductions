"""Tests for the 3-Coloring -> 1-in-3-SAT reduction."""

from __future__ import annotations

import random
from itertools import combinations

import problems
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    OneInThreeSat.validate(reduced)  # must be a valid target instance
    src = ThreeColoring.is_yes(instance)
    tgt = OneInThreeSat.is_yes(reduced)
    assert src == tgt, (
        f"MISMATCH source={src} target={tgt}\n"
        f"instance={instance}\nreduced={reduced}"
    )
    tests_passed += 1


def all_graphs(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield {
            "n": n,
            "edges": [list(p) for i, p in enumerate(pairs) if mask >> i & 1],
        }


def main():
    # 1. Exhaustive over all graphs with n = 0..5 (1024 at n=5).
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # 2. Random graphs, including larger n and sparse/dense regimes.
    rng = random.Random(12345)
    for trial in range(400):
        n = rng.randint(0, 9)
        p = rng.choice([0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
        edges = [
            [u, v]
            for u, v in combinations(range(n), 2)
            if rng.random() < p
        ]
        check({"n": n, "edges": edges})

    # 3. Specific edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    # K4 must be no.
    k4 = {"n": 4, "edges": [[u, v] for u, v in combinations(range(4), 2)]}
    check(k4)
    assert ThreeColoring.is_yes(k4) is False
    # K5 must be no.
    k5 = {"n": 5, "edges": [[u, v] for u, v in combinations(range(5), 2)]}
    check(k5)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
