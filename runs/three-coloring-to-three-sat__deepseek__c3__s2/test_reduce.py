"""Tests for the 3-Coloring -> 3-SAT reduction in reduce.py.

Compares the brute-force solvers from problems.py on small source instances
and their reductions, and checks that every reduced instance is a valid
3-SAT instance.
"""

from __future__ import annotations

import random

import problems
from problems import ThreeColoring, ThreeSat
from reduce import reduce

tests_run = 0
tests_passed = 0


def check(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    ThreeColoring.validate(instance)
    target = reduce(instance)
    # The reduction must produce a well-formed 3-SAT instance.
    ThreeSat.validate(target)
    expected = ThreeColoring.is_yes(instance)
    got = ThreeSat.is_yes(target)
    assert expected == got, (
        f"mismatch on {instance!r}: source={expected}, target={got}, "
        f"reduced={target!r}"
    )
    tests_passed += 1


def main() -> None:
    # 1. Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})  # K3, yes
    check({"n": 4, "edges": []})  # no edges, yes
    check(
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    )  # K4, no
    # K4 plus an isolated vertex, still no.
    check(
        {
            "n": 5,
            "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]],
        }
    )
    # Odd cycle (needs 3 colours) vs even cycle (2 colours).
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})
    check({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]})

    # 2. Exhaustive: every graph on 0..5 vertices.
    for instance in ThreeColoring.enumerate_instances(5):
        check(instance)

    # 3. Random graphs of various sizes and densities.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 9)
        p = rng.random()
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < p:
                    edges.append([u, v])
        check({"n": n, "edges": edges})

    # 4. Random instances from the problem's own generator.
    for scale in range(0, 9):
        for _ in range(40):
            check(ThreeColoring.random_instance(rng, scale))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
