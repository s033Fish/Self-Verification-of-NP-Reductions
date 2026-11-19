"""Independent tests for reduce.py: Hamiltonian Cycle -> SAT.

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import copy
import itertools
import random
import sys
import time

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def ham_bruteforce(instance: dict) -> bool:
    """Hamiltonian cycle by trying every cyclic ordering."""
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    edge_set = set()
    for u, v in edges:
        edge_set.add(frozenset((u, v)))
    for perm in itertools.permutations(range(1, n)):
        seq = (0,) + perm
        ok = True
        for i in range(n):
            if frozenset((seq[i], seq[(i + 1) % n])) not in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """SAT by enumerating every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        assign = [bool((bits >> (v - 1)) & 1) for v in range(1, m + 1)]
        good = True
        for clause in clauses:
            if not any(
                (lit > 0 and assign[abs(lit) - 1])
                or (lit < 0 and not assign[abs(lit) - 1])
                for lit in clause
            ):
                good = False
                break
        if good:
            return True
    return False


# A DPLL solver so we can also check larger reductions independently of
# brute force (still our own solver, no external libraries).

def sat_dpll(instance: dict) -> bool:
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, lit):
        out = []
        for c in clauses:
            if lit in c:
                continue
            nc = [x for x in c if x != -lit]
            if not nc:
                return None
            out.append(nc)
        return out

    def solve(clauses):
        if any(len(c) == 0 for c in clauses):
            return False
        while True:
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, unit)
            if clauses is None:
                return False
        if not clauses:
            return True
        all_lits = set(l for c in clauses for l in c)
        for l in all_lits:
            if -l not in all_lits:
                clauses = simplify(clauses, l)
                if clauses is None:
                    return False
                return solve(clauses)
        c = min(clauses, key=len)
        lit = c[0]
        for choice in (lit, -lit):
            sub = simplify(clauses, choice)
            if sub is not None and solve(sub):
                return True
        return False

    return solve(clauses)


# ----------------------------------------------------------------------
# Instance generators

def all_graphs(n: int):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for k, e in enumerate(possible) if (mask >> k) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver

def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label, sat_solver):
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = ham_bruteforce(instance)
        before = copy.deepcopy(instance)
        red = reduce(instance)
        if instance != before:
            failures.append((label, "reduce mutated its input"))
            return
        try:
            problems.Sat.validate(red)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, instance, red, f"invalid target: {exc}"))
            return
        got = sat_solver(red)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, instance, red, expected, got))

    # Exhaustive over all graphs for n = 0..4 (SAT brute force is cheap).
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}", sat_bruteforce)

    # Exhaustive over all graphs on 5 vertices (2^10 = 1024), DPLL.
    for g in all_graphs(5):
        check(g, "exhaustive n=5", sat_dpll)

    # Random larger graphs; use DPLL for the SAT side.
    rng = random.Random(12345)
    for n in (6, 7, 8):
        for trial in range(60):
            p = rng.choice([0.15, 0.25, 0.4, 0.55, 0.7, 0.9])
            g = random_graph(n, p, rng)
            check(g, f"random n={n} trial={trial}", sat_dpll)

    # Random graphs with randomly reversed edge orientations.
    for n in (4, 5, 6, 7):
        for trial in range(40):
            g = random_graph(n, rng.choice([0.3, 0.5, 0.8]), rng)
            g["edges"] = [e[::-1] if rng.random() < 0.5 else e for e in g["edges"]]
            check(g, f"reversed n={n} trial={trial}", sat_dpll if n >= 5 else sat_bruteforce)

    # Structured cases.
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "triangle", sat_bruteforce)
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]}, "path4", sat_bruteforce)
    check({"n": 3, "edges": [[0, 1], [1, 2]]}, "path3", sat_bruteforce)
    check({"n": 0, "edges": []}, "empty0", sat_bruteforce)
    check({"n": 1, "edges": []}, "single1", sat_bruteforce)
    check({"n": 2, "edges": [[0, 1]]}, "edge2", sat_bruteforce)
    for n in range(0, 9):
        g = {"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]}
        check(g, f"complete n={n}", sat_dpll if n >= 5 else sat_bruteforce)
    for n in range(3, 10):
        g = {"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]}
        check(g, f"cycle n={n}", sat_dpll if n >= 5 else sat_bruteforce)
    for n in range(3, 10):
        g = {"n": n, "edges": [[0, i] for i in range(1, n)]}
        check(g, f"star n={n}", sat_dpll if n >= 5 else sat_bruteforce)
    # Complete bipartite K_{a,b}: Hamiltonian cycle iff a == b >= 2.
    for a in range(1, 5):
        for b in range(1, 5):
            n = a + b
            edges = [[u, a + v] for u in range(a) for v in range(b)]
            check({"n": n, "edges": edges}, f"K{a},{b}", sat_dpll)

    # Exhaustive over all graphs on 6 vertices (2^15 = 32768), DPLL.
    import os
    if os.environ.get("EXHAUSTIVE6") == "1":
        for g in all_graphs(6):
            check(g, "exhaustive n=6", sat_dpll)

    # Sanity: reduction output size grows polynomially.
    sizes = []
    for n in (5, 10, 15, 20):
        g = random_graph(n, 0.5, random.Random(n))
        t0 = time.time()
        red = reduce(g)
        dt = time.time() - t0
        sizes.append((n, red["num_vars"], len(red["clauses"]), round(dt, 4)))
    print("size/timing (n, num_vars, num_clauses, seconds):")
    for s in sizes:
        print("  ", s)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print("  ", f)
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
