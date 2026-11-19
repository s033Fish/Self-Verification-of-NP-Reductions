"""Tests for reduce.py: compare brute-force solvers on small instances."""

import random

import problems
from problems import HamiltonianCycle, Sat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    HamiltonianCycle.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = HamiltonianCycle.is_yes(instance)
    got = Sat.is_yes(out)
    if expected == got:
        tests_passed += 1
    else:
        print("MISMATCH", instance, "expected", expected, "got", got)
        raise AssertionError(f"mismatch on {instance}")


def main():
    # Exhaustive over all graphs on 0..4 vertices.
    for instance in HamiltonianCycle.enumerate_instances(4):
        check(instance)

    # Random graphs on 5..8 vertices, several densities.
    rng = random.Random(12345)
    for n in range(5, 9):
        for _ in range(300):
            p = rng.random()
            edges = [
                [u, v]
                for u in range(n)
                for v in range(u + 1, n)
                if rng.random() < p
            ]
            check({"n": n, "edges": edges})

    # Structured cases: cycles, paths, complete graphs, empty graphs.
    for n in range(0, 9):
        check({"n": n, "edges": []})
        complete = [[u, v] for u in range(n) for v in range(u + 1, n)]
        check({"n": n, "edges": complete})
        if n >= 3:
            cycle = [[i, (i + 1) % n] for i in range(n)]
            check({"n": n, "edges": cycle})
            path = [[i, i + 1] for i in range(n - 1)]
            check({"n": n, "edges": path})

    # random_instance draws.
    for scale in range(0, 9):
        for _ in range(200):
            inst = HamiltonianCycle.random_instance(rng, scale)
            check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
