"""Exact solvers for both problems and tests for the reduction.

The 1-in-3-SAT solver uses backtracking (exact, not the naive 2^m brute
force) so that the reduced instances - which have 3n + 3|E| variables - can
be decided quickly.  A naive brute force is also provided and cross-checked
on tiny instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the definitions.

def solve_three_coloring(instance):
    """Return True iff the graph is 3-colourable (brute force 3^n)."""
    n = instance["n"]
    edges = instance["edges"]
    for colours in itertools.product(range(3), repeat=n):
        if all(colours[u] != colours[v] for u, v in edges):
            return True
    return False


def solve_one_in_three_sat_bruteforce(instance):
    """Naive 2^m brute force (only usable for tiny m)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(sum(1 for lit in clause if bits[lit - 1]) == 1 for clause in clauses):
            return True
    return False


def solve_one_in_three_sat(instance):
    """Exact backtracking solver for positive 1-in-3-SAT."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    # Precompute, for each clause, its variable indices (0-based).
    cl = [[lit - 1 for lit in clause] for clause in clauses]
    assignment = [None] * m

    def consistent():
        for a, b, c in cl:
            t = 0
            unassigned = 0
            for idx in (a, b, c):
                val = assignment[idx]
                if val is None:
                    unassigned += 1
                elif val:
                    t += 1
            if t > 1:
                return False
            if t == 0 and unassigned == 0:
                return False
        return True

    def backtrack():
        if not consistent():
            return False
        # pick an unassigned variable that occurs in a clause
        chosen = None
        for a, b, c in cl:
            for idx in (a, b, c):
                if assignment[idx] is None:
                    chosen = idx
                    break
            if chosen is not None:
                break
        if chosen is None:
            return True
        for value in (False, True):
            assignment[chosen] = value
            if backtrack():
                return True
            assignment[chosen] = None
        return False

    return backtrack()


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n):
    """All simple graphs on vertices 0..n-1."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def check(instance):
    """Validate, reduce, validate, and compare answers."""
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    OneInThreeSat.validate(reduced)
    src = solve_three_coloring(instance)
    tgt = solve_one_in_three_sat(reduced)
    return src, tgt


def main():
    tests_run = 0
    tests_passed = 0

    def record(ok):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if ok:
            tests_passed += 1
        return ok

    # 0. Cross-check the backtracking solver against naive brute force on
    #    many tiny random 1-in-3-SAT instances.
    rng = random.Random(999)
    for _ in range(400):
        m = rng.randint(0, 8)
        clauses = []
        if m >= 3:
            for _ in range(rng.randint(0, 6)):
                clauses.append(rng.sample(range(1, m + 1), 3))
        inst = {"num_vars": m, "clauses": clauses}
        OneInThreeSat.validate(inst)
        a = solve_one_in_three_sat(inst)
        b = solve_one_in_three_sat_bruteforce(inst)
        if not record(a == b):
            print("FAIL solver cross-check %r: backtrack=%s brute=%s" % (inst, a, b))

    # 1. Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            src, tgt = check(g)
            if not record(src == tgt):
                print("FAIL exhaustive n=%d %r: src=%s tgt=%s" % (n, g, src, tgt))

    # 2. Random graphs with up to 8 vertices.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 8)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < 0.5]
        g = {"n": n, "edges": edges}
        src, tgt = check(g)
        if not record(src == tgt):
            print("FAIL random %r: src=%s tgt=%s" % (g, src, tgt))

    # 3. Specific edge cases.
    cases = [
        {"n": 0, "edges": []},                                  # empty graph
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},            # triangle: yes
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3],
                           [1, 2], [1, 3], [2, 3]]},            # K4: no
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},  # C5: yes
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]},  # C6: yes
    ]
    for g in cases:
        src, tgt = check(g)
        if not record(src == tgt):
            print("FAIL edge case %r: src=%s tgt=%s" % (g, src, tgt))

    # 4. Explicitly confirm the documented edge cases.
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    assert solve_three_coloring(k4) is False
    assert solve_three_coloring({"n": 0, "edges": []}) is True
    assert solve_one_in_three_sat({"num_vars": 0, "clauses": []}) is True
    record(True)
    record(True)
    record(True)

    # 5. Structure / size sanity checks on the reduction.
    r = reduce({"n": 3, "edges": [[0, 1]]})
    assert r["num_vars"] == 3 * 3 + 3 * 1 == 12, r
    assert len(r["clauses"]) == 3 + 3 * 1 == 6, r
    record(True)

    print("tests_run=%d tests_passed=%d" % (tests_run, tests_passed))
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
