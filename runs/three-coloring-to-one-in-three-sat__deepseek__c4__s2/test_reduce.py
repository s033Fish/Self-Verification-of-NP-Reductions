"""Tests for reduce.py: 3-Coloring -> 1-in-3-SAT.

Contains independent brute-force solvers for both problems (written from the
docstrings in problems.py) and compares their answers on many small source
instances against the answers on the reduced instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------


def solve_3coloring(instance) -> bool:
    """True iff the graph is 3-colourable (brute force over 3^n colourings)."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_1in3(num_vars, clauses) -> bool:
    """True iff some assignment makes exactly one var true in every clause.

    DPLL with the natural 1-in-3 propagation rules (one true -> other two
    false; two false -> third true).  Exact.
    """
    clauses = [tuple(c) for c in clauses]

    def propagate(assign):
        assign = dict(assign)
        changed = True
        while changed:
            changed = False
            for a, b, c in clauses:
                vals = (assign.get(a), assign.get(b), assign.get(c))
                ntrue = sum(1 for v in vals if v is True)
                nfalse = sum(1 for v in vals if v is False)
                if ntrue > 1 or nfalse > 2:
                    return None
                if ntrue == 1:
                    for v in (a, b, c):
                        if assign.get(v) is None:
                            assign[v] = False
                            changed = True
                elif nfalse == 2:
                    for v in (a, b, c):
                        if assign.get(v) is None:
                            assign[v] = True
                            changed = True
        return assign

    def rec(assign):
        assign = propagate(assign)
        if assign is None:
            return False
        unassigned = [v for v in range(1, num_vars + 1) if assign.get(v) is None]
        if not unassigned:
            return True
        v = unassigned[0]
        for val in (True, False):
            nxt = dict(assign)
            nxt[v] = val
            if rec(nxt):
                return True
        return False

    return rec({})


def solve_target(instance) -> bool:
    return solve_1in3(instance["num_vars"], instance["clauses"])


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance, label=""):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    OneInThreeSat.validate(reduced)
    expected = solve_3coloring(instance)
    got = solve_target(reduced)
    if expected == got:
        TESTS_PASSED += 1
    else:
        print(f"FAIL {label}: source={instance} expected={expected} got={got}")
        print(f"     reduced={reduced}")


def all_graphs(n):
    """All simple graphs on n labelled vertices (all edge subsets)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main():
    # Exhaustive over all graphs with n <= 5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}")

    # Exhaustive-ish: all graphs with n = 6 but only a random sample of edges
    # is too many (2^15); instead test a deterministic sample plus all graphs
    # with a bounded number of edges.
    pairs6 = [(u, v) for u in range(6) for v in range(u + 1, 6)]
    for mask in range(1 << len(pairs6)):
        if bin(mask).count("1") > 4:
            continue
        edges = [list(pairs6[i]) for i in range(len(pairs6)) if mask >> i & 1]
        check({"n": 6, "edges": edges}, "n=6 few edges")

    # K4 and K5 must be no.
    k4 = {"n": 4, "edges": [[u, v] for u in range(4) for v in range(u + 1, 4)]}
    check(k4, "K4")
    k5 = {"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]}
    check(k5, "K5")

    # Random graphs of various sizes (including larger ones where the source
    # brute force is still feasible: 3^n).
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 8)
        p = rng.choice([0.0, 0.1, 0.25, 0.5, 0.8, 1.0])
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < p:
                    edges.append([u, v])
        check({"n": n, "edges": edges}, "random")

    # Explicit edge cases from the docstrings.
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "triangle")
    check({"n": 1, "edges": []}, "n=1")

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED, "some tests failed"
    return TESTS_RUN, TESTS_PASSED


if __name__ == "__main__":
    main()
