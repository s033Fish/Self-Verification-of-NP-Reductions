"""Independent tests for reduce.py: 3-Coloring -> 3-SAT.

Contains brute-force (exact) solvers for both problems written from the
definitions in problems.py, then compares the answer of many small source
instances with the answer of their reduction.

The solvers are themselves cross-checked against independent exhaustive
enumerators so that a bug in a solver cannot silently hide a bug in reduce.
"""

from __future__ import annotations

import copy
import itertools
import json
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)
# ----------------------------------------------------------------------

def solve_three_coloring(instance: dict) -> bool:
    """Exact 3-colourability via backtracking."""
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n

    def rec(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            if all(colour[j] != c for j in adj[i]):
                colour[i] = c
                if rec(i + 1):
                    return True
                colour[i] = -1
        return False

    return rec(0)


def solve_three_coloring_enumerate(instance: dict) -> bool:
    """Independent exhaustive check over all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for assign in itertools.product(range(3), repeat=n):
        if all(assign[u] != assign[v] for u, v in edges):
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """Exact 3-SAT via DPLL with unit propagation."""
    clauses = [tuple(c) for c in instance["clauses"]]

    def propagate(assign: dict) -> dict | None:
        changed = True
        while changed:
            changed = False
            for cl in clauses:
                unassigned = []
                satisfied = False
                for lit in cl:
                    val = assign.get(abs(lit))
                    if val is None:
                        unassigned.append(lit)
                    elif val == (lit > 0):
                        satisfied = True
                        break
                if satisfied:
                    continue
                if not unassigned:
                    return None
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    v, val = abs(lit), lit > 0
                    if v in assign:
                        if assign[v] != val:
                            return None
                    else:
                        assign[v] = val
                        changed = True
        return assign

    def rec(assign: dict) -> bool:
        assign = dict(assign)
        if propagate(assign) is None:
            return False
        var = next((abs(l) for cl in clauses for l in cl if abs(l) not in assign), None)
        if var is None:
            return True
        return any(rec({**assign, var: val}) for val in (True, False))

    return rec({})


def solve_three_sat_enumerate(instance: dict) -> bool:
    """Independent exhaustive check over all 2^m assignments."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(any(bits[abs(l) - 1] == (l > 0) for l in cl) for cl in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def check(instance: dict, results: list) -> None:
    problems.SOURCE.validate(instance)

    # Solver cross-check (only feasible for small n).
    if instance["n"] <= 8:
        assert solve_three_coloring(instance) == solve_three_coloring_enumerate(instance)

    src = solve_three_coloring(instance)
    frozen = copy.deepcopy(instance)
    target = reduce(instance)
    assert instance == frozen, "reduce must not mutate its input"

    problems.TARGET.validate(target)
    if target["num_vars"] <= 12:
        assert solve_three_sat(target) == solve_three_sat_enumerate(target)
    tgt = solve_three_sat(target)

    results.append(src == tgt)
    if src != tgt:
        print("MISMATCH")
        print("  source:", instance)
        print("  source answer:", src)
        print("  target answer:", tgt)
        print("  target:", target)


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield {"n": n, "edges": [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]}


def main() -> None:
    results: list[bool] = []

    # Exhaustive over every graph on 0..4 vertices (all 1+1+2+8+64 graphs).
    for n in range(0, 5):
        for inst in all_graphs(n):
            check(inst, results)

    # Explicit edge cases.
    check({"n": 0, "edges": []}, results)                       # yes
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, results)  # K3 -> yes
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, results)  # K4 -> no
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}, results)  # C5 -> yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]}, results)  # C4 -> yes

    # Random graphs on 5..8 vertices (n=8 uses DPLL, no enumeration).
    rng = random.Random(12345)
    for n in (5, 6, 7, 8):
        pairs = list(itertools.combinations(range(n), 2))
        for _ in range(150):
            edges = [list(p) for p in pairs if rng.random() < 0.5]
            check({"n": n, "edges": edges}, results)

    tests_run = len(results)
    tests_passed = sum(1 for r in results if r)
    verdict = {
        "verified": tests_run > 0 and tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
