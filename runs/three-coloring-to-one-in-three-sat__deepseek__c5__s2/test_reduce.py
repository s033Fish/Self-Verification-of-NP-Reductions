"""Independent verification of reduce.py (3-Coloring -> 1-in-3-SAT).

We implement our own exact solvers for both problems from the definitions,
generate many small source instances, reduce them, and compare answers.
"""
from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force / exact solvers written from the problem definitions.

def solve_three_coloring(instance):
    """True iff the graph is 3-colourable. Brute force over 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


def solve_one_in_three(instance):
    """True iff exactly one variable per clause can be made true.

    Exact backtracking search (DPLL-style) over variables 1..m.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    def rec(assign):
        # Constraint propagation to a fixpoint.
        while True:
            changed = False
            for clause in clauses:
                true_count = sum(1 for v in clause if assign[v] is True)
                if true_count > 1:
                    return False
                if true_count == 1:
                    for v in clause:
                        if assign[v] is None:
                            assign[v] = False
                            changed = True
                else:  # true_count == 0
                    unassigned = [v for v in clause if assign[v] is None]
                    if not unassigned:
                        return False
                    if len(unassigned) == 1:
                        assign[unassigned[0]] = True
                        changed = True
            if not changed:
                break
        # Choose next unassigned variable.
        nxt = next((i for i in range(1, m + 1) if assign[i] is None), None)
        if nxt is None:
            return True
        for value in (True, False):
            branch = assign[:]
            branch[nxt] = value
            if rec(branch):
                return True
        return False

    return rec([None] * (m + 1))


# ----------------------------------------------------------------------
# Instance generators.

def all_graphs(n):
    """All simple graphs on n labelled vertices (no loops, no duplicate edges)."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests.

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(source_instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # Validate the source instance against the official validator.
        ThreeColoring.validate(source_instance)
        src_answer = solve_three_coloring(source_instance)
        target_instance = reduce(source_instance)
        # The reduction must produce a well-formed target instance.
        OneInThreeSat.validate(target_instance)
        tgt_answer = solve_one_in_three(target_instance)
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            failures.append((label, source_instance, src_answer, target_instance, tgt_answer))

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, f"all_graphs n={n}")

    # Random graphs with n = 6, 7, 8 (sampled, since exhaustive is large).
    rng = random.Random(12345)
    for n in (6, 7, 8):
        for _ in range(400):
            p = rng.choice([0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9])
            check(random_graph(n, p, rng), f"random n={n}")

    # Specific structural edge cases.
    check({"n": 0, "edges": []}, "empty graph")
    check({"n": 1, "edges": []}, "single vertex")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "triangle (yes)")
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4 (no)")
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}, "C5 (yes)")
    # K4 plus an isolated vertex -> still no.
    check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4 + isolated (no)")
    # Odd wheel-like / Petersen graph (3-colourable? Petersen is 3-chromatic -> yes).
    petersen = {"n": 10, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0],
                                   [5, 7], [7, 9], [9, 6], [6, 8], [8, 5],
                                   [0, 5], [1, 6], [2, 7], [3, 8], [4, 9]]}
    check(petersen, "Petersen (yes)")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, src, sa, tgt, ta in failures[:10]:
            print("  ", label, "src=", src, "src_ans=", sa, "tgt_ans=", ta)
    else:
        print("All tests passed.")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
