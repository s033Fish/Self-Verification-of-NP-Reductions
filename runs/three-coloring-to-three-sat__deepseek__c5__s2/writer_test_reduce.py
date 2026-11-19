"""Tests comparing brute-force answers on small 3-Coloring instances with
the answers on their reductions to 3-SAT."""

from __future__ import annotations

import itertools
import json
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import solve_coloring, solve_sat

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    target = reduce(instance)
    TARGET.validate(target)
    expected = solve_coloring(instance)
    got = solve_sat(target)
    if expected != got:
        raise AssertionError(
            f"mismatch on {instance}: coloring={expected}, sat={got}, "
            f"reduction={target}"
        )
    tests_passed += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main():
    # Exhaustive over all graphs with up to 4 vertices.
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # Explicit K4 must be unsatisfiable.
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    check(k4)
    assert solve_coloring(k4) is False
    assert solve_sat(reduce(k4)) is False

    # Empty graph is always yes.
    check({"n": 0, "edges": []})
    check({"n": 5, "edges": []})

    # Random graphs on 5..7 vertices.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(5, 7)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        check({"n": n, "edges": edges})

    # Random sparse graphs (likely colour-able) on 5..8 vertices.
    for _ in range(200):
        n = rng.randint(5, 8)
        pairs = list(itertools.combinations(range(n), 2))
        rng.shuffle(pairs)
        k = rng.randint(0, min(len(pairs), n))
        edges = [list(p) for p in pairs[:k]]
        check({"n": n, "edges": edges})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    verified = tests_run == tests_passed
    with open("verdict.json", "w") as f:
        json.dump(
            {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed},
            f,
        )
    assert verified


if __name__ == "__main__":
    main()
