"""Independent verification of reduce.py: 3-Coloring -> positive 1-in-3-SAT.

We implement our own brute-force / backtracking solvers for both problems
directly from the definitions in problems.py, cross-check those solvers
against naive enumeration, then compare the source answer with the target
answer of reduce() on many small instances.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers (written from the problem definitions; no use of reduce.py)
# ----------------------------------------------------------------------

def solve_three_coloring(instance):
    """Backtracking 3-colourability."""
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n

    def bt(v):
        if v == n:
            return True
        for c in range(3):
            if all(colour[w] != c for w in adj[v]):
                colour[v] = c
                if bt(v + 1):
                    return True
                colour[v] = -1
        return False

    return bt(0)


def solve_one_in_three(instance):
    """Backtracking solver for positive 1-in-3-SAT (exactly one true/clause)."""
    clauses = [tuple(c) for c in instance["clauses"]]
    assign = {}

    def propagate():
        changed = True
        while changed:
            changed = False
            for cl in clauses:
                true_cnt = 0
                unassigned = []
                for var in cl:
                    if var in assign:
                        if assign[var]:
                            true_cnt += 1
                    else:
                        unassigned.append(var)
                if true_cnt > 1:
                    return False
                if true_cnt == 1:
                    for var in unassigned:
                        assign[var] = False
                        changed = True
                else:  # true_cnt == 0
                    if not unassigned:
                        return False
                    if len(unassigned) == 1:
                        assign[unassigned[0]] = True
                        changed = True
        return True

    def bt():
        if not propagate():
            return False
        target = None
        for cl in clauses:
            if any(v not in assign for v in cl):
                for v in cl:
                    if v not in assign:
                        target = v
                        break
                break
        if target is None:
            return True
        for val in (True, False):
            saved = dict(assign)
            assign[target] = val
            if bt():
                return True
            assign.clear()
            assign.update(saved)
        return False

    return bt()


# ----------------------------------------------------------------------
# Naive reference solvers (pure enumeration), used to sanity-check above
# ----------------------------------------------------------------------

def naive_three_coloring(instance):
    n = instance["n"]
    for colour in itertools.product(range(3), repeat=n):
        if all(colour[u] != colour[v] for u, v in instance["edges"]):
            return True
    return False


def naive_one_in_three(instance):
    m = instance["num_vars"]
    for bits in itertools.product((False, True), repeat=m):
        if all(sum(1 for v in cl if bits[v - 1]) == 1 for cl in instance["clauses"]):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = [[u, v] for u in range(n) for v in range(u + 1, n) if rng.random() < p]
    return {"n": n, "edges": edges}


def random_one_in_three(m, k, rng):
    clauses = []
    for _ in range(k):
        if m < 3:
            break
        clauses.append(sorted(rng.sample(range(1, m + 1), 3)))
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def record(ok, info=""):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if ok:
            tests_passed += 1
        else:
            failures.append(info)

    rng = random.Random(20240517)

    # --- Sanity check solvers against naive enumeration -------------------
    for n in range(0, 6):
        for g in all_graphs(n):
            record(solve_three_coloring(g) == naive_three_coloring(g), ("3col", g))
    for _ in range(300):
        m = rng.randint(0, 8)
        k = rng.randint(0, 8)
        f = random_one_in_three(m, k, rng)
        record(solve_one_in_three(f) == naive_one_in_three(f), ("1in3", f))

    # --- Main comparison: source answer == reduced target answer ----------
    def check(src):
        SOURCE.validate(src)
        tgt = reduce(src)
        TARGET.validate(tgt)
        expected = solve_three_coloring(src)
        got = solve_one_in_three(tgt)
        record(expected == got, (src, tgt, expected, got))

    # Exhaustive over all graphs for n = 0..5
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random graphs n = 6..9
    for n in range(6, 10):
        for _ in range(80):
            p = rng.choice([0.15, 0.3, 0.5, 0.7, 0.9])
            check(random_graph(n, p, rng))

    # Structured cases
    for n in range(0, 10):
        check({"n": n, "edges": []})
        check({"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]})
    for n in range(3, 10):
        check({"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]})
    # K4 must be no
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    check(k4)
    record(solve_three_coloring(k4) is False, ("K4-not-3colourable",))

    result = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(result, f)

    if failures:
        print("FAILURES:", len(failures))
        for info in failures[:5]:
            print("  ", info)
    print("tests_run =", tests_run, "tests_passed =", tests_passed)
    print("verdict:", result)


if __name__ == "__main__":
    main()
