"""Tests for the 3-Coloring -> SAT reduction."""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, Sat
from reduce import reduce
from solvers import solve_three_coloring, solve_sat

tests_run = 0
tests_passed = 0


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = solve_three_coloring(instance)
    got = solve_sat(reduced)
    if expected == got:
        tests_passed += 1
    else:
        raise AssertionError(
            f"mismatch {label}: source={instance} expected={expected} "
            f"reduced={reduced} got={got}"
        )


def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


# Exhaustive over all graphs with 0..5 vertices.
for n in range(0, 5):
    for g in all_graphs(n):
        check(g, f"exhaustive n={n}")

# Random larger graphs (n up to 8) to exercise more structure.
rng = random.Random(12345)
for _ in range(150):
    n = rng.randint(0, 7)
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(pairs)
    k = rng.randint(0, len(pairs))
    edges = [list(p) for p in pairs[:k]]
    check({"n": n, "edges": edges}, "random")

# Explicit edge cases from the docstrings.
check({"n": 0, "edges": []}, "n=0")
check({"n": 1, "edges": []}, "n=1")
check({"n": 2, "edges": [[0, 1]]}, "n=2")
check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "K3")
check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4")
check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}, "C5")

# The reduced formula for n=0 must be the empty, satisfiable formula.
assert reduce({"n": 0, "edges": []}) == {"num_vars": 0, "clauses": []}

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
