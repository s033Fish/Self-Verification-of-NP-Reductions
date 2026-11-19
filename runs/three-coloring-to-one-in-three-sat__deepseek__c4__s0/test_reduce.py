"""Tests for the 3-Coloring -> 1-in-3-SAT reduction.

Contains independent brute-force solvers for both problems (written from the
definitions in problems.py) and compares their answers on many small source
instances against the reduction's output.
"""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers

def solve_three_coloring(instance: dict) -> bool:
    """Brute force: try all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colouring[u] == colouring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_one_in_three(instance: dict) -> bool:
    """Backtracking solver for positive 1-in-3-SAT.

    Exhaustive in the worst case but prunes with simple propagation so that
    the small instances used here are tractable.
    """
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]

    occ = {v: [] for v in range(1, m + 1)}
    for ci, clause in enumerate(clauses):
        for v in clause:
            occ[v].append(ci)

    val = [None] * (m + 1)
    trail: list[int] = []

    def propagate() -> bool:
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                t = 0
                u = 0
                uv = None
                for v in clause:
                    if val[v] is True:
                        t += 1
                    elif val[v] is None:
                        u += 1
                        uv = v
                if t > 1:
                    return False
                if t == 1:
                    if u == 0:
                        continue
                    for v in clause:
                        if val[v] is None:
                            val[v] = False
                            trail.append(v)
                            changed = True
                else:  # t == 0
                    if u == 0:
                        return False
                    if u == 1:
                        val[uv] = True
                        trail.append(uv)
                        changed = True
        return True

    def undo(mark: int) -> None:
        while len(trail) > mark:
            v = trail.pop()
            val[v] = None

    def rec() -> bool:
        mark = len(trail)
        if not propagate():
            undo(mark)
            return False
        v = None
        for i in range(1, m + 1):
            if val[i] is None and occ[i]:
                v = i
                break
        if v is None:
            undo(mark)
            return True
        for choice in (True, False):
            mark2 = len(trail)
            val[v] = choice
            trail.append(v)
            if rec():
                undo(mark2)
                return True
            undo(mark2)
        undo(mark)
        return False

    return rec()


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n: int):
    """Yield every simple graph on n vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(instance)
        expected = solve_three_coloring(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)
        got = solve_one_in_three(reduced)
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", instance, "expected", expected, "got", got)
            print("reduced:", reduced)

    # Edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})

    # All graphs on 0..4 vertices.
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # Random graphs on 5..6 vertices.
    rng = random.Random(12345)
    for n in (5, 6):
        for _ in range(150):
            check(random_graph(n, rng.uniform(0.0, 1.0), rng))

    # Random graphs on 7..8 vertices.
    for n in (7, 8):
        for _ in range(40):
            check(random_graph(n, rng.uniform(0.1, 0.9), rng))

    # Odd cycles (not 3-colourable) and even cycles (3-colourable).
    for k in range(3, 13):
        edges = [[i, (i + 1) % k] for i in range(k)]
        check({"n": k, "edges": edges})

    # Explicit K4 (and K4 plus isolated vertices) must be no.
    for extra in range(4):
        n = 4 + extra
        edges = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
        check({"n": n, "edges": edges})

    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    assert solve_three_coloring(k4) is False
    assert solve_one_in_three(reduce(k4)) is False

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
