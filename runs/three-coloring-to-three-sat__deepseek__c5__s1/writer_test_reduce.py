"""Solvers for both problems and tests for reduce().

Run:  python3 test_reduce.py

We provide two independent solvers for each problem:
  * a plain brute-force enumerator (used on tiny instances), and
  * a backtracking / DPLL solver (used on larger instances).
Both are written from the problem definitions; no external solver is used.
"""

from __future__ import annotations

import itertools
import random
import sys
import time

from problems import ThreeColoring, ThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# 3-Coloring solvers.

def solve_three_coloring_bruteforce(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    for colours in itertools.product(range(3), repeat=n):
        if all(colours[u] != colours[v] for u, v in edges):
            return True
    return False


def solve_three_coloring(instance: dict) -> bool:
    """Exact backtracking 3-colouring solver."""
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n

    def bt(v: int) -> bool:
        if v == n:
            return True
        used = {colour[w] for w in adj[v] if colour[w] != -1}
        for c in range(3):
            if c not in used:
                colour[v] = c
                if bt(v + 1):
                    return True
                colour[v] = -1
        return False

    return bt(0)


# ----------------------------------------------------------------------
# 3-SAT solvers.

def solve_three_sat_bruteforce(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(
            any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in c)
            for c in clauses
        ):
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """Exact DPLL solver with unit propagation for 3-SAT."""
    clauses = [tuple(c) for c in instance["clauses"]]

    def simplify(clauses, var, val):
        out = []
        for c in clauses:
            if any((l > 0) == val for l in c if abs(l) == var):
                continue
            rest = tuple(l for l in c if abs(l) != var)
            if not rest:
                return None
            out.append(rest)
        return out

    def dpll(clauses):
        changed = True
        while changed:
            changed = False
            for c in clauses:
                if len(c) == 1:
                    l = c[0]
                    clauses = simplify(clauses, abs(l), l > 0)
                    if clauses is None:
                        return False
                    changed = True
                    break
        if not clauses:
            return True
        counts = {}
        for c in clauses:
            for l in c:
                counts[abs(l)] = counts.get(abs(l), 0) + 1
        v = max(counts, key=counts.get)
        for val in (True, False):
            s = simplify(clauses, v, val)
            if s is not None and dpll(s):
                return True
        return False

    return dpll(clauses)


# ----------------------------------------------------------------------
# Instance generators.

def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def random_3sat(m: int, k: int, rng: random.Random) -> dict:
    if m < 3:
        k = 0
    clauses = []
    for _ in range(k):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests.

def main() -> int:
    tests_run = 0
    tests_passed = 0

    def check(name: str, condition: bool) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1
        else:
            print(f"FAIL: {name}")

    # --- Cross-check the two solver implementations on tiny instances. ---
    rng = random.Random(999)
    for _ in range(200):
        n = rng.randint(0, 6)
        g = random_graph(n, rng.random(), rng)
        check("coloring solvers agree",
              solve_three_coloring(g) == solve_three_coloring_bruteforce(g))
    for _ in range(200):
        m = rng.randint(0, 8)
        s = random_3sat(m, rng.randint(0, 10), rng)
        check("sat solvers agree",
              solve_three_sat(s) == solve_three_sat_bruteforce(s))

    # --- Sanity checks on the solvers. ---
    check("n=0 yes", solve_three_coloring({"n": 0, "edges": []}) is True)
    check("n=3 triangle yes",
          solve_three_coloring({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}) is True)
    check("K4 no",
          solve_three_coloring({"n": 4, "edges": [[0, 1], [0, 2], [0, 3],
                                                  [1, 2], [1, 3], [2, 3]]}) is False)
    check("empty formula yes", solve_three_sat({"num_vars": 0, "clauses": []}) is True)
    check("trivial unsat",
          solve_three_sat({"num_vars": 3,
                           "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
                                       [-1, -2, 3], [-1, 2, -3], [1, -2, -3],
                                       [-1, -2, -3]]}) is False)

    # --- Reduction preserves the answer on ALL graphs up to 4 vertices. ---
    for n in range(0, 5):
        for g in all_graphs(n):
            ThreeColoring.validate(g)
            r = reduce(g)
            ThreeSat.validate(r)  # must be a valid 3-SAT instance
            src = solve_three_coloring(g)
            tgt = solve_three_sat(r)
            check(f"all_graphs n={n} edges={g['edges']}", src == tgt)

    # --- Random graphs up to 8 vertices (both solvers). ---
    for _ in range(600):
        n = rng.randint(0, 8)
        g = random_graph(n, rng.random(), rng)
        ThreeColoring.validate(g)
        r = reduce(g)
        ThreeSat.validate(r)
        check(f"random graph n={n}", solve_three_coloring(g) == solve_three_sat(r))

    # --- Edge cases explicitly required. ---
    check("reduce n=0 valid", ThreeSat.validate(reduce({"n": 0, "edges": []})) is None)
    check("reduce n=0 yes", solve_three_sat(reduce({"n": 0, "edges": []})) is True)
    for n in (1, 2, 3):
        g = {"n": n, "edges": [[u, v] for u in range(n) for v in range(u + 1, n)]}
        check(f"K{n} yes", solve_three_coloring(g) is True)
        check(f"reduce K{n} yes", solve_three_sat(reduce(g)) is True)
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    check("reduce K4 no", solve_three_sat(reduce(k4)) is False)

    # --- Structural checks on the produced instance. ---
    r = reduce(k4)
    check("num_vars = 3n+1", r["num_vars"] == 3 * 4 + 1)
    check("all clauses 3 literals", all(len(c) == 3 for c in r["clauses"]))
    check("all clauses distinct vars",
          all(len({abs(l) for l in c}) == 3 for c in r["clauses"]))
    check("no zero literals",
          all(l != 0 and abs(l) <= r["num_vars"] for c in r["clauses"] for l in c))

    # --- Reduction must be fast (polynomial) on a larger graph. ---
    big = random_graph(80, 0.3, rng)
    t0 = time.time()
    rb = reduce(big)
    dt = time.time() - t0
    check("large graph reduction fast", dt < 5.0)
    ThreeSat.validate(rb)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if tests_run == tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())
