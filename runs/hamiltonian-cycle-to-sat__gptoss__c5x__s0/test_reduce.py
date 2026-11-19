"""Independent tests for reduce.py: Hamiltonian Cycle -> SAT.

We implement our own brute-force / DPLL solvers for both problems from the
definitions in problems.py, then compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import HamiltonianCycle, Sat, InvalidInstance
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solver for Hamiltonian Cycle (undirected simple graph).
def hc_brute(instance) -> bool:
    n = instance["n"]
    if n <= 2:
        return False
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    start = 0
    # Backtracking search for a Hamiltonian cycle starting at vertex 0.
    def dfs(path, used):
        last = path[-1]
        if len(path) == n:
            return start in adj[last]
        for nxt in range(n):
            if nxt not in used and nxt in adj[last]:
                used.add(nxt)
                path.append(nxt)
                if dfs(path, used):
                    return True
                path.pop()
                used.remove(nxt)
        return False
    return dfs([start], {start})


# ----------------------------------------------------------------------
# Brute-force solver for SAT (only for small num_vars).
def sat_brute(instance) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            if not any(
                (bits >> (abs(lit) - 1)) & 1 == (1 if lit > 0 else 0)
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# DPLL solver for SAT (handles larger reduced instances).
def sat_dpll(instance) -> bool:
    m = instance["num_vars"]
    clauses = [tuple(dict.fromkeys(c)) for c in instance["clauses"]]
    if any(len(c) == 0 for c in clauses):
        return False

    def simplify(clauses, assign):
        # assign: dict var -> bool
        new = []
        for clause in clauses:
            sat = False
            rest = []
            for lit in clause:
                v = abs(lit)
                if v in assign:
                    if assign[v] == (lit > 0):
                        sat = True
                        break
                else:
                    rest.append(lit)
            if sat:
                continue
            if not rest:
                return None  # conflict
            new.append(tuple(rest))
        return new

    def unit_propagate(clauses, assign):
        while True:
            unit = None
            for clause in clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                return clauses, assign
            v = abs(unit)
            val = unit > 0
            if v in assign:
                if assign[v] != val:
                    return None, None
                # already assigned; remove satisfied clauses
                clauses = simplify(clauses, assign)
                if clauses is None:
                    return None, None
                continue
            assign = dict(assign)
            assign[v] = val
            clauses = simplify(clauses, assign)
            if clauses is None:
                return None, None

    def dpll(clauses, assign):
        res = unit_propagate(clauses, assign)
        clauses, assign = res
        if clauses is None:
            return None
        if not clauses:
            return assign
        # choose a variable from the first clause
        lit = clauses[0][0]
        v = abs(lit)
        for val in (True, False):
            a2 = dict(assign)
            a2[v] = val
            c2 = simplify(clauses, a2)
            if c2 is None:
                continue
            r = dpll(c2, a2)
            if r is not None:
                return r
        return None

    return dpll(clauses, {}) is not None


# ----------------------------------------------------------------------
def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def check(instance, results):
    src = hc_brute(instance)
    red = reduce_mod.reduce(instance)
    # validate reduced instance
    Sat.validate(red)
    tgt = sat_dpll(red)
    # cross-check DPLL against brute force when feasible
    if red["num_vars"] <= 18:
        bf = sat_brute(red)
        assert bf == tgt, ("dpll/brute mismatch", red, bf, tgt)
    results["run"] += 1
    if src == tgt:
        results["pass"] += 1
    else:
        results["fail"].append((instance, src, tgt, red))


def main():
    random.seed(12345)
    results = {"run": 0, "pass": 0, "fail": []}

    # Exhaustive small graphs.
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g, results)

    # Random larger graphs.
    for n in range(5, 9):
        pairs = list(itertools.combinations(range(n), 2))
        for _ in range(300):
            p = random.random()
            edges = [list(e) for e in pairs if random.random() < p]
            check({"n": n, "edges": edges}, results)

    # Some structured cases: complete graph, cycle graph, path.
    for n in range(3, 9):
        complete = {"n": n, "edges": [list(e) for e in itertools.combinations(range(n), 2)]}
        cyc = {"n": n, "edges": [[i, (i + 1) % n] for i in range(n)]}
        path = {"n": n, "edges": [[i, i + 1] for i in range(n - 1)]}
        for g in (complete, cyc, path):
            check(g, results)

    print("tests_run =", results["run"])
    print("tests_passed =", results["pass"])
    if results["fail"]:
        print("FAILURES:", len(results["fail"]))
        for inst, s, t, red in results["fail"][:5]:
            print("  instance:", inst, "source:", s, "target:", t)
        sys.exit(1)
    print("ALL OK")


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------
# Independent Held-Karp style DP Hamiltonian cycle check (different algorithm
# from the backtracking solver above), used to cross-validate hc_brute.
def hc_held_karp(instance) -> bool:
    n = instance["n"]
    if n <= 2:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = adj[v][u] = True
    # dp[mask][v] = True if there is a path starting at 0, visiting exactly
    # the vertices in mask, ending at v.  Then check edge v-0.
    full = 1 << n
    dp = [0] * (full * n)  # bitmask of reachable endpoints
    dp[(1 << 0) * n + 0] = 1
    for mask in range(full):
        if not (mask & 1):
            continue
        for v in range(n):
            if not (dp[mask * n + v] & 1):
                continue
            for w in range(n):
                if mask & (1 << w):
                    continue
                if adj[v][w]:
                    dp[(mask | (1 << w)) * n + w] = 1
    last = full - 1
    return any(dp[last * n + v] and adj[v][0] for v in range(n))


def cross_check_solvers():
    random.seed(999)
    for n in range(0, 9):
        pairs = list(itertools.combinations(range(n), 2))
        for _ in range(200):
            edges = [list(e) for e in pairs if random.random() < random.random()]
            g = {"n": n, "edges": edges}
            assert hc_brute(g) == hc_held_karp(g), ("HC solver mismatch", g)
    print("HC solver cross-check OK")


if __name__ == "__main__":
    cross_check_solvers()
    main()
