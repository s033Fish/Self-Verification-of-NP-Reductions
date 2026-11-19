"""Brute-force solvers for both problems plus tests for reduce.py."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def solve_hamiltonian_cycle(instance: dict) -> bool:
    n = instance["n"]
    if n <= 2:
        return False
    edge_set = set()
    for u, v in instance["edges"]:
        edge_set.add((u, v) if u < v else (v, u))
    if n == 3:
        # only the triangle works
        return all(
            (min(a, b), max(a, b)) in edge_set
            for a, b in [(0, 1), (1, 2), (0, 2)]
        )
    # fix vertex 0 as the start; try all orders of the remaining vertices
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        order = (0,) + perm
        ok = True
        for i in range(n):
            a = order[i]
            b = order[(i + 1) % n]
            if (min(a, b), max(a, b)) not in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """Complete DPLL SAT solver (sound and complete)."""
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

        # check all clauses satisfied
        if all(
            any(abs(l) in assignment and assignment[abs(l)] == (l > 0) for l in c)
            for c in clauses
        ):
            return True

        # choose an unassigned variable
        var = None
        for clause in clauses:
            for lit in clause:
                if abs(lit) not in assignment:
                    var = abs(lit)
                    break
            if var is not None:
                break
        if var is None:
            return True

        for value in (True, False):
            new_assign = dict(assignment)
            new_assign[var] = value
            if dpll(clauses, new_assign):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Instance generators

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
# Tests

def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.HamiltonianCycle.validate(instance)
        expected = solve_hamiltonian_cycle(instance)
        reduced = reduce(instance)
        problems.Sat.validate(reduced)
        got = solve_sat(reduced)
        assert got == expected, (
            f"MISMATCH for {instance}: hc={expected}, sat={got}, "
            f"reduced={reduced}"
        )
        tests_passed += 1

    # --- edge cases ---
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 2, "edges": [[0, 1]]})
    check({"n": 2, "edges": []})
    check({"n": 3, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2]]})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})

    # --- exhaustive small graphs ---
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g)

    # --- exhaustive n=5 (2^10 = 1024 graphs) ---
    for g in all_graphs(5):
        check(g)

    # --- random larger graphs ---
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(3, 8)
        p = rng.choice([0.2, 0.35, 0.5, 0.65, 0.8])
        check(random_graph(n, p, rng))

    # --- structured: complete graphs and cycles (should be yes) ---
    for n in range(3, 9):
        complete = {"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]}
        check(complete)
        ring = {"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]}
        check(ring)

    # --- structured: paths (should be no for n >= 3) ---
    for n in range(3, 9):
        path = {"n": n, "edges": [[i, i + 1] for i in range(n - 1)]}
        check(path)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)


if __name__ == "__main__":
    main()
