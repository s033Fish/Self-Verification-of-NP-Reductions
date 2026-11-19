"""Tests for the 3-Coloring -> SAT reduction.

Contains brute-force solvers for both problems (directly from the
docstrings) plus a DPLL SAT solver used for larger instances.  The DPLL
solver is cross-checked against the brute-force solver on small formulas.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeColoring, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_coloring(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_sat_bruteforce(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# DPLL SAT solver (correct, handles the larger reductions quickly).

def solve_sat(instance: dict) -> bool:
    def simplify(clauses, lit):
        """Apply literal lit = true; return simplified clause list or None if
        an empty clause appears."""
        result = []
        for clause in clauses:
            if lit in clause:
                continue
            reduced = [l for l in clause if l != -lit]
            if not reduced:
                return None
            result.append(reduced)
        return result

    def dpll(clauses):
        while True:
            unit = None
            for clause in clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, unit)
            if clauses is None:
                return False
        if not clauses:
            return True
        lit = clauses[0][0]
        for choice in (lit, -lit):
            reduced = simplify(clauses, choice)
            if reduced is not None and dpll(reduced):
                return True
        return False

    clauses = [list(c) for c in instance["clauses"]]
    if any(len(c) == 0 for c in clauses):
        return False
    return dpll(clauses)


# ----------------------------------------------------------------------
# Instance generation.

def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests.

def check(instance: dict) -> None:
    ThreeColoring.validate(instance)
    target = reduce(instance)
    Sat.validate(target)
    src = solve_three_coloring(instance)
    tgt = solve_sat(target)
    assert src == tgt, (instance, target, src, tgt)


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(name, fn):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            fn()
        except AssertionError as exc:
            print(f"FAIL {name}: {exc}")
        else:
            tests_passed += 1

    # Cross-check the DPLL solver against brute force on small formulas.
    rng = random.Random(999)
    for _ in range(200):
        m = rng.randint(0, 5)
        clauses = []
        for _ in range(rng.randint(0, 6)):
            k = rng.randint(0, 3)
            clause = []
            for _ in range(k):
                v = rng.randint(1, m) if m else 0
                if v == 0:
                    continue
                clause.append(v if rng.random() < 0.5 else -v)
            clauses.append(clause)
        inst = {"num_vars": m, "clauses": clauses}
        Sat.validate(inst)
        assert solve_sat(inst) == solve_sat_bruteforce(inst), inst
    run("dpll vs bruteforce", lambda: None)

    # Edge cases.
    run("n=0", lambda: check({"n": 0, "edges": []}))
    run("n=1", lambda: check({"n": 1, "edges": []}))
    run("n=2 edge", lambda: check({"n": 2, "edges": [[0, 1]]}))
    run("n=3 triangle", lambda: check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}))
    run("K4", lambda: check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}))

    # Exhaustive over all graphs on up to 5 vertices.
    for n in range(0, 6):
        def make(n=n):
            for g in all_graphs(n):
                check(g)
        run(f"all graphs n={n}", make)

    # Random graphs, including larger ones.
    for trial in range(500):
        n = rng.randint(0, 9)
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.8, 1.0])
        g = random_graph(n, p, rng)
        run(f"random {trial} n={n} p={p}", lambda g=g: check(g))

    # Structured cases.
    run("K5", lambda: check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]}))
    run("K6", lambda: check({"n": 6, "edges": [[u, v] for u in range(6) for v in range(u + 1, 6)]}))
    run("cycle C7", lambda: check({"n": 7, "edges": [[i, (i + 1) % 7] for i in range(7)]}))
    run("odd cycle C5", lambda: check({"n": 5, "edges": [[i, (i + 1) % 5] for i in range(5)]}))
    run("bipartite K3,3", lambda: check({
        "n": 6,
        "edges": [[i, 3 + j] for i in range(3) for j in range(3)],
    }))
    run("grid 3x3", lambda: check({
        "n": 9,
        "edges": [[r * 3 + c, r * 3 + c + 1] for r in range(3) for c in range(2)]
        + [[r * 3 + c, (r + 1) * 3 + c] for r in range(2) for c in range(3)],
    }))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    with open("verdict.json", "w") as fh:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, fh)


if __name__ == "__main__":
    main()
