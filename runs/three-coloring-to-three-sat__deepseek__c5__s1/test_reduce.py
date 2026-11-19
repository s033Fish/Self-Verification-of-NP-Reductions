"""Independent tests for reduce.py: 3-Coloring -> 3-SAT.

We implement our own brute-force solvers from the problem definitions in
problems.py, then compare solver answers on many small source instances and
their reductions.  We also validate every produced target instance, check the
reduction does not mutate its input, and cross-check the fast solvers against
naive exhaustive ones.
"""

from __future__ import annotations

import copy
import itertools
import random

from problems import SOURCE, TARGET
import reduce as reduce_module


# ----------------------------------------------------------------------
# Solvers for 3-Coloring
# ----------------------------------------------------------------------

def solve_three_coloring(instance: dict) -> bool:
    """Backtracking solver."""
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n

    def bt(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            if all(color[j] != c for j in adj[i]):
                color[i] = c
                if bt(i + 1):
                    return True
                color[i] = -1
        return False

    return bt(0)


def solve_three_coloring_naive(instance: dict) -> bool:
    """Exhaustive over all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for assign in itertools.product(range(3), repeat=n):
        if all(assign[u] != assign[v] for u, v in edges):
            return True
    return False


# ----------------------------------------------------------------------
# Solvers for 3-SAT
# ----------------------------------------------------------------------

def solve_three_sat(instance: dict) -> bool:
    """DPLL with unit propagation."""
    clauses = [tuple(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        clauses = [list(c) for c in clauses]
        while True:
            new_clauses = []
            unit = None
            for c in clauses:
                sat = False
                unassigned = []
                for lit in c:
                    v = abs(lit)
                    if v in assignment:
                        if (lit > 0) == assignment[v]:
                            sat = True
                            break
                    else:
                        unassigned.append(lit)
                if sat:
                    continue
                if not unassigned:
                    return False
                if len(unassigned) == 1 and unit is None:
                    unit = unassigned[0]
                new_clauses.append(unassigned)
            clauses = new_clauses
            if unit is None:
                break
            v = abs(unit)
            assignment[v] = (unit > 0)
        if not clauses:
            return True
        lit = clauses[0][0]
        v = abs(lit)
        for val in (True, False):
            a2 = dict(assignment)
            a2[v] = val
            if dpll(clauses, a2):
                return True
        return False

    return dpll(clauses, {})


def solve_three_sat_naive(instance: dict) -> bool:
    """Exhaustive over all 2^m assignments."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any(((lit > 0) == bits[abs(lit) - 1]) for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return {"n": n, "edges": edges}


def random_3sat(m: int, k: int, rng: random.Random):
    clauses = []
    for _ in range(k):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    def record(ok: bool, info: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if ok:
            tests_passed += 1
        else:
            failures.append(info)

    # --- Cross-validate the fast solvers against naive ones. ---
    rng = random.Random(999)
    for n in range(0, 8):
        for _ in range(30):
            g = random_graph(n, rng.choice([0.0, 0.2, 0.5, 0.8, 1.0]), rng)
            record(solve_three_coloring(g) == solve_three_coloring_naive(g),
                   f"coloring solver mismatch on {g}")
    for m in range(0, 9):
        for _ in range(30):
            if m < 3:
                f = {"num_vars": m, "clauses": []}
            else:
                f = random_3sat(m, rng.randint(0, 12), rng)
            record(solve_three_sat(f) == solve_three_sat_naive(f),
                   f"sat solver mismatch on {f}")

    # --- Core reduction check. ---
    def check(inst: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            SOURCE.validate(inst)
        except Exception as e:  # pragma: no cover
            failures.append(f"invalid source instance {inst}: {e}")
            return
        snapshot = copy.deepcopy(inst)
        reduced = reduce_module.reduce(inst)
        if inst != snapshot:
            failures.append(f"reduce mutated its input: {inst}")
            return
        try:
            TARGET.validate(reduced)
        except Exception as e:
            failures.append(f"invalid target instance from {inst}: {e} -> {reduced}")
            return
        # Determinism.
        if reduce_module.reduce(inst) != reduced:
            failures.append(f"reduce not deterministic on {inst}")
            return
        expected = solve_three_coloring(inst)
        got = solve_three_sat(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append(f"mismatch on {inst}: expected {expected}, got {got}")

    # Exhaustive over all graphs with n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # Explicit edge cases.
    check({"n": 0, "edges": []})
    check({"n": 1, "edges": []})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})            # triangle: yes
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3],
                             [1, 2], [1, 3], [2, 3]]})             # K4: no
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})     # C4: yes
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})  # C5: no
    check({"n": 6, "edges": [[0, 1], [1, 2], [2, 0],
                             [3, 4], [4, 5], [5, 3]]})             # 2 triangles: yes

    # Random graphs for larger n, various densities.
    for n in range(6, 10):
        for p in (0.0, 0.15, 0.3, 0.5, 0.7, 0.9, 1.0):
            for _ in range(50):
                check(random_graph(n, p, rng))

    # Random sparse graphs (more likely colorable) for n up to 11.
    for n in range(9, 12):
        for _ in range(40):
            check(random_graph(n, 0.12, rng))

    print(f"tests_run = {tests_run}")
    print(f"tests_passed = {tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for info in failures[:20]:
            print("  ", info)
    else:
        print("All tests passed.")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
