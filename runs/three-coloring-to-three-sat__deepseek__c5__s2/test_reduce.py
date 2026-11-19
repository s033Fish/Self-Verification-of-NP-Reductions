"""Independent tests for reduce.py: 3-Coloring -> 3-SAT.

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small instances.
"""

import itertools
import json
import random

from problems import ThreeColoring, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def solve_3coloring(instance):
    """Return True iff the graph is 3-colourable (brute force)."""
    n = instance["n"]
    edges = instance["edges"]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n

    def bt(i):
        if i == n:
            return True
        for c in range(3):
            ok = True
            for w in adj[i]:
                if color[w] == c:
                    ok = False
                    break
            if ok:
                color[i] = c
                if bt(i + 1):
                    return True
                color[i] = -1
        return False

    return bt(0)


def solve_3sat(instance):
    """Return True iff the 3-CNF is satisfiable (DPLL + unit propagation)."""
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, var, val):
        new = []
        for cl in clauses:
            if (var if val else -var) in cl:
                continue  # clause satisfied
            nc = [l for l in cl if l != (-var if val else var)]
            if not nc:
                return None  # conflict
            new.append(nc)
        return new

    def dpll(clauses):
        while True:
            unit = None
            for cl in clauses:
                if len(cl) == 1:
                    unit = cl[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, abs(unit), unit > 0)
            if clauses is None:
                return False
        if not clauses:
            return True
        var = abs(clauses[0][0])
        for val in (True, False):
            nc = simplify(clauses, var, val)
            if nc is not None and dpll(nc):
                return True
        return False

    return dpll(clauses)


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    rng = random.Random(12345)
    instances = []

    # Exhaustive: every graph on 0..5 vertices.
    for n in range(0, 6):
        instances.extend(all_graphs(n))

    # Explicit edge cases.
    instances.append({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})  # K4
    instances.append({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]})  # K5
    instances.append({"n": 6, "edges": [[u, v] for u in range(6) for v in range(u + 1, 6)]})  # K6
    instances.append({"n": 0, "edges": []})
    instances.append({"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]})
    instances.append({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})

    # Random graphs on 6..8 vertices (covers larger padding-variable usage).
    for n in (6, 7, 8):
        for _ in range(150):
            instances.append(random_graph(n, rng.uniform(0.1, 0.9), rng))

    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in instances:
        tests_run += 1
        try:
            ThreeColoring.validate(inst)
            reduced = reduce(inst)
            ThreeSat.validate(reduced)
            src = solve_3coloring(inst)
            tgt = solve_3sat(reduced)
            ok = (src == tgt)
        except Exception as exc:  # noqa: BLE001
            ok = False
            src = tgt = None
            failures.append((inst, "exception: %r" % (exc,)))
        if ok:
            tests_passed += 1
        else:
            if len(failures) < 10:
                failures.append((inst, (src, tgt)))

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    if failures:
        print("FAILURES:")
        for f in failures:
            print("  ", f)

    verified = (tests_run == tests_passed) and tests_run > 0
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
    print("verdict.json written:", verified)


if __name__ == "__main__":
    main()
