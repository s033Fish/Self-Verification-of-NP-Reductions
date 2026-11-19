"""Tests for the 3-Coloring -> 3-SAT reduction.

We implement brute-force / DPLL solvers for both problems from the
definitions in problems.py, generate many small source instances, reduce
them, and compare answers.  Every reduced instance is also checked with the
TARGET validator.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeColoring, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers (written from the problem definitions)

def solve_three_coloring(instance: dict) -> bool:
    """Brute force over 3^n colourings."""
    ThreeColoring.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """DPLL with unit propagation."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # assignment: dict var -> bool
        while True:
            # unit propagation
            unit = None
            for clause in clauses:
                unassigned = []
                satisfied = False
                for lit in clause:
                    v = abs(lit)
                    if v in assignment:
                        if assignment[v] == (lit > 0):
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)
                if satisfied:
                    continue
                if not unassigned:
                    return False  # conflict
                if len(unassigned) == 1:
                    unit = unassigned[0]
                    break
            if unit is None:
                break
            v = abs(unit)
            assignment[v] = (unit > 0)

        # choose an unassigned variable
        var = None
        for clause in clauses:
            for lit in clause:
                v = abs(lit)
                if v not in assignment:
                    var = v
                    break
            if var is not None:
                break
        if var is None:
            return True  # all clauses satisfied

        for value in (True, False):
            new_assignment = dict(assignment)
            new_assignment[var] = value
            if dpll(clauses, new_assignment):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(rng: random.Random, n: int, p: float) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(src: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        tgt = reduce(src)
        ThreeSat.validate(tgt)  # must be a valid target instance
        a = solve_three_coloring(src)
        b = solve_three_sat(tgt)
        if a != b:
            raise AssertionError(
                f"MISMATCH src={src} src_ans={a} tgt={tgt} tgt_ans={b}"
            )
        tests_passed += 1

    # Edge case n = 0.
    check({"n": 0, "edges": []})

    # Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random graphs, including larger ones (DPLL handles them).
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 12)
        p = rng.choice([0.1, 0.3, 0.5, 0.8])
        check(random_graph(rng, n, p))

    # Structured cases.
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})  # K4 no
    check({"n": 3, "edges": [[0, 1], [0, 2], [1, 2]]})                            # K3 yes
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})            # C5 no
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})                    # C4 yes
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]}) # K5 no
    check({"n": 6, "edges": [[0, 1], [2, 3], [4, 5]]})                            # yes
    check({"n": 0, "edges": []})

    # Check the empty formula case target is valid too.
    t0 = reduce({"n": 0, "edges": []})
    assert t0["clauses"] == []
    assert solve_three_sat(t0) is True

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)


if __name__ == "__main__":
    main()
