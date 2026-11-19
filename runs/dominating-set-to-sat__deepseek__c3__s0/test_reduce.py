"""Tests for reduce.py: compare DominatingSet.is_yes with Sat.is_yes on the
reduction, over many small source instances (including edge cases)."""
import itertools
import random

import problems
from problems import DominatingSet, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    DominatingSet.validate(instance)
    target = reduce(instance)
    Sat.validate(target)
    expected = DominatingSet.is_yes(instance)
    got = Sat.is_yes(target)
    assert expected == got, (
        f"MISMATCH instance={instance} expected={expected} got={got} "
        f"target={target}"
    )
    tests_passed += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if mask >> i & 1]


def main():
    # Exhaustive over all graphs for n = 0..5 and all relevant k.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random graphs for larger n.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        edges = [
            [u, v]
            for u, v in itertools.combinations(range(n), 2)
            if rng.random() < rng.choice([0.1, 0.3, 0.5, 0.8])
        ]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Use the problem's own random_instance generator too.
    for scale in range(0, 10):
        for _ in range(200):
            inst = DominatingSet.random_instance(rng, scale)
            check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
