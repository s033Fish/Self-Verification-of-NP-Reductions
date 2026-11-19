"""Independent tests for reduce.py: NAE-3-SAT -> 3-Coloring.

problems.py provides no solvers, so we implement our own solvers for both
problems from the docstrings, then compare the answer of each small source
instance with the answer of its reduction.  The reduction output is also
validated against problems.TARGET.validate.

The 3-colouring solver is DSATUR with forward checking and colour-symmetry
breaking (fix vertex 0 to colour 0).  It is an exact search, just with strong
pruning, so the reduced graphs (much larger than the source instances) can be
decided quickly.
"""
from __future__ import annotations

import itertools
import random
import time

from problems import NaeThreeSat, ThreeColoring
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Exact solvers (independent of reduce.py)
# ----------------------------------------------------------------------

def nae3sat_solve(instance):
    """Return True iff the NAE-3-SAT instance is satisfiable (brute force)."""
    NaeThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            values = []
            for lit in clause:
                v = abs(lit)
                val = bool((bits >> (v - 1)) & 1)
                values.append(val if lit > 0 else (not val))
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


def three_coloring_solve(instance):
    """Exact 3-colourability via DSATUR + forward checking + symmetry break."""
    ThreeColoring.validate(instance)
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)

    color = [-1] * n
    avail = [set(range(3)) for _ in range(n)]

    def propagate(v, c):
        undo = []
        color[v] = c
        for w in adj[v]:
            if color[w] == -1 and c in avail[w]:
                avail[w].discard(c)
                undo.append(w)
                if not avail[w]:
                    return undo, False
        return undo, True

    def undo_propagate(v, c, undo):
        for w in undo:
            avail[w].add(c)
        color[v] = -1

    def select():
        best = -1
        best_sat = -1
        best_deg = -1
        for v in range(n):
            if color[v] == -1:
                sat = 3 - len(avail[v])
                deg = len(adj[v])
                if (sat, deg) > (best_sat, best_deg):
                    best_sat, best_deg, best = sat, deg, v
        return best

    def backtrack():
        v = select()
        if v == -1:
            return True
        for c in sorted(avail[v]):
            undo, ok = propagate(v, c)
            if ok and backtrack():
                return True
            undo_propagate(v, c, undo)
        return False

    if n == 0:
        return True
    # break colour symmetry: vertex 0 gets colour 0
    undo, ok = propagate(0, 0)
    if ok and backtrack():
        return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_clauses(num_vars):
    """All canonical 3-literal clauses on 3 distinct variables (all signs)."""
    clauses = []
    for vars_ in itertools.combinations(range(1, num_vars + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            clauses.append([s * v for s, v in zip(signs, vars_)])
    return clauses


def check_instance(inst):
    """Return (source_answer, target_answer, reduced_instance)."""
    src_ans = nae3sat_solve(inst)
    red = reduce_mod.reduce(inst)
    ThreeColoring.validate(red)  # reduction output must be a valid target
    tgt_ans = three_coloring_solve(red)
    return src_ans, tgt_ans, red


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            src_ans, tgt_ans, red = check_instance(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, inst, "EXCEPTION: %r" % (exc,)))
            return
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append((label, inst, (src_ans, tgt_ans, red)))

    # ---- edge cases -------------------------------------------------
    run({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    run({"num_vars": 1, "clauses": []}, "m=1 no clauses")
    run({"num_vars": 2, "clauses": []}, "m=2 no clauses")
    run({"num_vars": 5, "clauses": []}, "m=5 no clauses")
    run({"num_vars": 3, "clauses": [[1, 2, 3]]}, "m=3 single clause")
    run({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "clause + complement")
    run({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]}, "3 clauses m=3")
    # all 8 clauses over 3 vars: forces every variable to be both true and false
    run({"num_vars": 3, "clauses": all_clauses(3)}, "all 8 clauses m=3 (unsat)")

    # ---- exhaustive m=3, all subsets of the 8 canonical clauses -----
    clauses3 = all_clauses(3)
    for r in range(len(clauses3) + 1):
        for combo in itertools.combinations(clauses3, r):
            run({"num_vars": 3, "clauses": [list(c) for c in combo]},
                "exhaustive m=3 subset")

    # ---- exhaustive m=4, subsets up to size 3 -----------------------
    clauses4 = all_clauses(4)
    for r in range(4):
        for combo in itertools.combinations(clauses4, r):
            run({"num_vars": 4, "clauses": [list(c) for c in combo]},
                "exhaustive m=4 subset<=3")

    # ---- random tests, various m and clause counts ------------------
    rng = random.Random(12345)
    for _ in range(4000):
        m = rng.randint(3, 6)
        nclauses = rng.randint(0, 10)
        cl = []
        for _ in range(nclauses):
            vs = rng.sample(range(1, m + 1), 3)
            cl.append([rng.choice((1, -1)) * v for v in vs])
        run({"num_vars": m, "clauses": cl}, "random")

    # ---- random m=7 with moderate clause counts ---------------------
    for _ in range(400):
        m = 7
        nclauses = rng.randint(0, 9)
        cl = []
        for _ in range(nclauses):
            vs = rng.sample(range(1, m + 1), 3)
            cl.append([rng.choice((1, -1)) * v for v in vs])
        run({"num_vars": m, "clauses": cl}, "random m=7")

    # ---- literal order permutations ---------------------------------
    for _ in range(500):
        m = rng.randint(3, 6)
        cl = []
        for _ in range(rng.randint(1, 5)):
            vs = rng.sample(range(1, m + 1), 3)
            lits = [rng.choice((1, -1)) * v for v in vs]
            rng.shuffle(lits)
            cl.append(lits)
        run({"num_vars": m, "clauses": cl}, "random-shuffled")

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    if failures:
        print("FAILURES:", len(failures))
        for label, inst, info in failures[:10]:
            print("  ", label, inst, info)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run, passed, fails = main()
    if fails:
        raise SystemExit(1)
