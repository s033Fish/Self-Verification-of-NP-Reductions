"""Independent tests for reduce.py: Dominating Set -> SAT.

We implement our own brute-force solvers from the problem definitions and
compare the answer of each source instance with the answer of its reduction.
No solver from problems.py / reduce.py is used (they provide none).
"""
from __future__ import annotations

import itertools
import random
import time

from problems import DominatingSet, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for Dominating Set (exhaustive over subsets <= k).
def brute_dominating(inst):
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, min(k, n) + 1):
        for comb in itertools.combinations(range(n), size):
            D = set(comb)
            if all(v in D or (adj[v] & D) for v in range(n)):
                return True
    return False


# Minimum dominating set size, computed independently by brute force.
def min_dominating_size(n, edges):
    if n == 0:
        return 0
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, n + 1):
        for comb in itertools.combinations(range(n), size):
            D = set(comb)
            if all(v in D or (adj[v] & D) for v in range(n)):
                return size
    return n


# ----------------------------------------------------------------------
# Brute-force solver for SAT: enumerate all assignments (small m only).
def brute_sat_enum(inst):
    m = inst["num_vars"]
    clauses = inst["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Exact DPLL solver (used for larger instances); cross-checked below.
def dpll_sat(inst):
    clauses = [list(c) for c in inst["clauses"]]

    def simplify(clauses, var, val):
        out = []
        for c in clauses:
            if (var if val else -var) in c:
                continue
            out.append([l for l in c if l != (-var if val else var)])
        return out

    def dpll(clauses):
        while True:
            unit = None
            for c in clauses:
                if len(c) == 0:
                    return False
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, abs(unit), unit > 0)
        vars_left = {abs(l) for c in clauses for l in c}
        if not vars_left:
            return True
        v = min(vars_left)
        return any(dpll(simplify(clauses, v, val)) for val in (True, False))

    return dpll(clauses)


def all_graphs(n):
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield [list(e) for i, e in enumerate(possible) if mask >> i & 1]


def main():
    tests_run = 0
    tests_passed = 0
    failures = []
    rng = random.Random(12345)

    def record(ok, info):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if ok:
            tests_passed += 1
        else:
            failures.append(info)

    # 1) Cross-check DPLL against enumeration on random small formulas.
    for _ in range(3000):
        m = rng.randint(0, 6)
        clauses = []
        for _ in range(rng.randint(0, 6)):
            length = rng.randint(0, 3)
            if m == 0:
                clauses.append([])
            else:
                clauses.append([rng.choice([-1, 1]) * rng.randint(1, m) for _ in range(length)])
        inst = {"num_vars": m, "clauses": clauses}
        a, b = brute_sat_enum(inst), dpll_sat(inst)
        record(a == b, ("dpll-crosscheck", inst, a, b))

    # 2) Exhaustive n = 0..5, all graphs, all k in -2..n+2, using the
    #    independent minimum-dominating-size oracle.
    for n in range(0, 6):
        for edges in all_graphs(n):
            d = min_dominating_size(n, edges)
            for k in range(-2, n + 3):
                src = {"n": n, "edges": edges, "k": k}
                DominatingSet.validate(src)
                tgt = reduce(src)
                Sat.validate(tgt)
                want = d <= k
                got = dpll_sat(tgt)
                record(want == got, (src, tgt, want, got, d))

    # 3) Random n = 6..8, all k.
    for _ in range(300):
        n = rng.randint(6, 8)
        possible = list(itertools.combinations(range(n), 2))
        edges = [list(e) for e in possible if rng.random() < 0.35]
        d = min_dominating_size(n, edges)
        for k in range(-1, n + 2):
            src = {"n": n, "edges": edges, "k": k}
            DominatingSet.validate(src)
            tgt = reduce(src)
            Sat.validate(tgt)
            record((d <= k) == dpll_sat(tgt), (src, tgt, d <= k, dpll_sat(tgt), d))

    # 4) Random n = 9..11 (exercises the Sinz branch), all k.
    for _ in range(120):
        n = rng.randint(9, 11)
        possible = list(itertools.combinations(range(n), 2))
        edges = [list(e) for e in possible if rng.random() < 0.3]
        d = min_dominating_size(n, edges)
        for k in range(-1, n + 2):
            src = {"n": n, "edges": edges, "k": k}
            DominatingSet.validate(src)
            tgt = reduce(src)
            Sat.validate(tgt)
            record((d <= k) == dpll_sat(tgt), (src, tgt, d <= k, dpll_sat(tgt), d))

    # 5) Explicit edge cases from the docstrings.
    edge_cases = [
        ({"n": 0, "edges": [], "k": 0}, True),
        ({"n": 0, "edges": [], "k": 5}, True),
        ({"n": 0, "edges": [], "k": -1}, False),
        ({"n": 1, "edges": [], "k": 0}, False),  # isolated vertex needs itself
        ({"n": 1, "edges": [], "k": 1}, True),
        ({"n": 2, "edges": [], "k": 1}, False),   # two isolated vertices
        ({"n": 2, "edges": [], "k": 2}, True),
        ({"n": 2, "edges": [[0, 1]], "k": 1}, True),
        ({"n": 3, "edges": [[0, 1]], "k": 1}, False),  # vertex 2 isolated
        ({"n": 3, "edges": [[0, 1]], "k": 2}, True),
        ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2}, True),
        ({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 1}, False),
    ]
    for src, want in edge_cases:
        DominatingSet.validate(src)
        tgt = reduce(src)
        Sat.validate(tgt)
        got = dpll_sat(tgt)
        record(want == got and want == brute_dominating(src), (src, tgt, want, got))

    # 6) Reduction must be polynomial: output size grows polynomially.
    t0 = time.time()
    for n in (20, 40, 80):
        edges = [[i, (i + 1) % n] for i in range(n)]
        tgt = reduce({"n": n, "edges": edges, "k": n // 2})
        Sat.validate(tgt)
        # output vars/clauses bounded by O(n^2)
        assert tgt["num_vars"] <= 2 * n * n + 10, tgt["num_vars"]
        assert len(tgt["clauses"]) <= 4 * n * n + 10, len(tgt["clauses"])
    record(time.time() - t0 < 5.0, ("polynomial-size",))

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:10]:
        print("FAIL:", f)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
