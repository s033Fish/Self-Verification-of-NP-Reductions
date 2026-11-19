"""Independent tests for reduce.py (3-Coloring -> SAT).

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare the answer of every small source
instance with the answer of its reduction.
"""

from __future__ import annotations

import itertools
import json
import random
from typing import Dict, List

from problems import ThreeColoring, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for 3-Coloring
# ----------------------------------------------------------------------

def solve_three_coloring(instance: Dict) -> bool:
    ThreeColoring.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# DPLL solver for SAT
# ----------------------------------------------------------------------

def solve_sat(instance: Dict) -> bool:
    Sat.validate(instance)
    clauses: List[set] = []
    for clause in instance["clauses"]:
        s = set(clause)
        if any(-lit in s for lit in s):
            continue  # tautology, always satisfied
        clauses.append(s)
    if any(len(c) == 0 for c in clauses):
        return False

    def dpll(clauses: List[set], assignment: Dict[int, bool]) -> bool:
        while True:
            new_clauses = []
            for clause in clauses:
                satisfied = False
                unassigned = []
                for lit in clause:
                    var = abs(lit)
                    if var in assignment:
                        if (lit > 0) == assignment[var]:
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)
                if satisfied:
                    continue
                if not unassigned:
                    return False
                new_clauses.append(set(unassigned))
            clauses = new_clauses
            units = [c for c in clauses if len(c) == 1]
            if not units:
                break
            for c in units:
                lit = next(iter(c))
                var = abs(lit)
                val = lit > 0
                if var in assignment and assignment[var] != val:
                    return False
                assignment[var] = val
        if not clauses:
            return True
        # choose a literal from the first clause
        lit = next(iter(clauses[0]))
        var = abs(lit)
        for val in (True, False):
            a2 = dict(assignment)
            a2[var] = val
            if dpll([set(c) for c in clauses], a2):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n: int):
    vertices = list(range(n))
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: Dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        src_answer = solve_three_coloring(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)  # reduction must produce a valid SAT instance
        tgt_answer = solve_sat(reduced)
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            failures.append((instance, src_answer, reduced, tgt_answer))

    # Exhaustive: every graph on 0..5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Random graphs on 6..10 vertices.
    rng = random.Random(12345)
    for n in range(6, 11):
        for _ in range(150):
            p = rng.choice([0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
            check(random_graph(n, p, rng))

    # A few specific edge cases.
    check({"n": 0, "edges": []})
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})  # K4 -> no
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})  # C5 -> yes

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:5]:
        print("FAIL:", f)

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print(json.dumps(verdict))


if __name__ == "__main__":
    main()
