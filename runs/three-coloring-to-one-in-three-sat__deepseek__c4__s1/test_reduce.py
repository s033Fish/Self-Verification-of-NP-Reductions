"""Tests comparing brute-force answers on small 3-Coloring instances and
their 1-in-3-SAT reductions."""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce
from solvers import three_coloring_solve, one_in_three_solve

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    ThreeColoring.validate(instance)
    target = reduce(instance)
    OneInThreeSat.validate(target)
    src = three_coloring_solve(instance)
    tgt = one_in_three_solve(target)
    if src == tgt:
        tests_passed += 1
    else:
        print("FAIL", label, instance, "src=", src, "tgt=", tgt, target)
        raise AssertionError(f"mismatch: {label} {instance}")


def all_graphs(n):
    """All simple graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def main():
    # Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}")

    # Exhaustive over all graphs with 6 vertices is 2^15 = 32768, fine.
    for g in all_graphs(6):
        check(g, "exhaustive n=6")

    # Random larger graphs.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(7, 10)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.4:
                    edges.append([u, v])
        check({"n": n, "edges": edges}, "random")

    # Edge cases explicitly.
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 1, "edges": []}, "n=1")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "triangle")
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4")
    check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]}, "K5")

    # No-clause target edge case sanity (m=0 formula is yes).
    assert one_in_three_solve({"num_vars": 0, "clauses": []}) is True
    assert one_in_three_solve({"num_vars": 3, "clauses": []}) is True

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
